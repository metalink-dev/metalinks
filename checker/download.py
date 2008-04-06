############# download functions #############

import os.path

class URL:
    def __init__(self, url, location = "", preference = "", maxconnections = ""):
        if preference == "":
            preference = 1
        if maxconnections == "":
            maxconnections = 1
        
        self.url = url
        self.location = location
        self.preference = int(preference)
        self.maxconnections = int(maxconnections)

def get(src, path, checksums = {}, force = False, handler = None):
    '''
    Download a file, decodes metalinks.
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected MD5SUM
    Fourth parameter, optional, expected SHA1SUM
    Fifth parameter, optional, force a new download even if a valid copy already exists
    Sixth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''

    if src.endswith(".metalink"):
        return download_metalink(src, path, force, handler)
    else:
        # parse out filename portion here
        filename = os.path.basename(src)
        result = download_file([src], os.path.join(path, filename), 0, checksums, force, handler)
        if result:
            return [result]
        return False

def download_file(urllist, local_file, size=0, checksums={}, force = False, handler = None, segmented = True, chunksums = {}, chunk_size = None):
    '''
    Download a file.
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, expected MD5SUM
    Fourth parameter, optional, expected SHA1SUM
    Fifth parameter, optional, force a new download even if a valid copy already exists
    Sixth parameter, optional, progress handler callback
    Returns file path if download is successful
    Returns False otherwise (checksum fails)
    '''
    print ""
    print "Downloading", os.path.basename(local_file)

    if os.path.exists(local_file) and (not force) and len(checksums) > 0:
        checksum = verify_checksum(local_file, checksums)
        if checksum:
            if size == 0:
                size = os.stat(local_file).st_size
            handler(1, size, size)
            #print ""
            return local_file
        else:
            print "Checksum failed for %s, retrying." % os.path.basename(local_file)

    directory = os.path.dirname(local_file)
    if not os.path.isdir(directory):
        os.makedirs(directory)

    seg_result = False
    if segmented:
        if chunk_size == None:
            chunk_size = 262144
        manager = Segment_Manager(urllist, local_file, size, reporthook = handler, chunksums = chunksums, chunk_size = int(chunk_size))
        seg_result = manager.run()
        
        if not seg_result:
            #seg_result = verify_checksum(local_file, checksums)
            print "\nCould not download all segments of the file, trying one mirror at a time."

    if (not segmented) or (not seg_result):
        # do it the old way
        # choose a random url tag to start with
        #urllist = list(urllist)
        #number = int(random.random() * len(urllist))
        urllist = start_sort(urllist)
        number = 0
        
        error = True
        count = 1
        while (error and (count <= len(urllist))):
            remote_file = complete_url(urllist[number])
            result = True
            try:
                urlretrieve(remote_file, local_file, handler)
            except:
                result = False
            error = not result
            number = (number + 1) % len(urllist)
            count += 1

    if verify_checksum(local_file, checksums):
        if size == 0:
            size = os.stat(local_file).st_size
        handler(1, size, size)
        #print ""
        return local_file
    else:
        print "\nChecksum failed for %s." % os.path.basename(local_file)

    return False

def download_metalink(src, path, force = False, handler = None):
    '''
    Decode a metalink file, can be local or remote
    First parameter, file to download, URL or file path to download from
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''
    src = complete_url(src)
    datasource = urllib2.urlopen(src)
    dom2 = xml.dom.minidom.parse(datasource)   # parse an open file
    datasource.close()

    metalink_node = get_subnodes(dom2, ["metalink"])
    try:
        metalink_type = get_attr_from_item(metalink_node, "type")
    except AttributeError:
        metalink_type = None
    if metalink_type == "dynamic":
        origin = get_attr_from_item(metalink_node, "origin")
        if origin != src:
            print "Downloading update from", origin
            return download_metalink(origin, path, force, handler)
    
    urllist = get_subnodes(dom2, ["metalink", "files", "file"])
    if len(urllist) == 0:
        #print "No urls to download file from."
        return False

    results = []
    for filenode in urllist:
        ostag = get_xml_tag_strings(filenode, ["os"])
        langtag = get_xml_tag_strings(filenode, ["language"])
            
        if OS == None or len(ostag) == 0 or ostag[0].lower() == OS.lower():
            if LANG == None or len(langtag) == 0 or langtag[0].lower() == LANG.lower():
                result = download_file_node(filenode, path, force, handler)
                if result:
                    results.append(result)

    return results

def download_file_node(item, path, force = False, handler = None):
    '''
    Downloads a specific version of a program
    First parameter, file XML node
    Second parameter, file path to save to
    Third parameter, optional, force a new download even if a valid copy already exists
    Fouth parameter, optional, progress handler callback
    Returns list of file paths if download(s) is successful
    Returns False otherwise (checksum fails)
    '''

    #urllist = get_xml_tag_strings(item, ["resources", "url"])
    urllist = {}
    for node in get_subnodes(item, ["resources", "url"]):
        url = get_xml_item_strings([node])[0]
        location = get_attr_from_item(node, "location")
        preference = get_attr_from_item(node, "preference")
        maxconnections = get_attr_from_item(node, "maxconnections")
        urllist[url] = URL(url, location, preference, maxconnections)
        
    if len(urllist) == 0:
        print "No urls to download file from."
        return False
            
    hashlist = get_subnodes(item, ["verification", "hash"])
    try:
        size = get_xml_tag_strings(item, ["size"])[0]
    except:
        size = 0
    
    hashes = {}
    for hashitem in hashlist:
        hashes[get_attr_from_item(hashitem, "type")] = hashitem.firstChild.nodeValue.strip()

    local_file = get_attr_from_item(item, "name")
    localfile = path_join(path, local_file)

    #extract chunk checksum information
    try:
        chunksize = int(get_attr_from_item(get_subnodes(item, ["verification", "pieces"])[0], "length"))
    except IndexError:
        chunksize = None

    chunksums = {}
    for piece in get_subnodes(item, ["verification", "pieces"]):
        hashtype = get_attr_from_item(piece, "type")
        chunksums[hashtype] = []
        for chunk in get_xml_tag_strings(piece, ["hash"]):
            chunksums[hashtype].append(chunk)

    return download_file(urllist, localfile, size, hashes, force, handler, SEGMENTED, chunksums, chunksize)

def complete_url(url):
    '''
    If no transport is specified in typical URL form, we assume it is a local
    file, perhaps only a relative path too.
    First parameter, string to convert to URL format
    Returns, string converted to URL format
    '''
    if get_transport(url) == "":
        absfile = os.path.abspath(url)
        if absfile[0] != "/":
            absfile = "/" + absfile
        return "file://" + absfile
    return url

def urlretrieve(url, filename, reporthook = None):
    '''
    modernized replacement for urllib.urlretrieve() for use with proxy
    '''
    block_size = 4096
    i = 0
    counter = 0
    temp = urllib2.urlopen(url)
    headers = temp.info()
    
    try:
        size = int(headers['Content-Length'])
    except KeyError:
        size = 0

    data = open(filename, 'wb')
    block = True

    ### FIXME need to check contents from previous download here
    resume = FileResume(filename + ".temp")
    resume.add_block(0)
    
    while block:
        block = temp.read(block_size)
        data.write(block)
        i += block_size
        counter += 1

        resume.set_block_size(counter * block_size)
                        
        if reporthook != None:
            #print counter, block_size, size
            reporthook(counter, block_size, size)

    resume.complete()
            
    data.close()
    temp.close()

    return (filename, headers)


class FileResume:
    '''
    Manages the resume data file
    '''
    def __init__(self, filename):
        self.size = 0
        self.blocks = []
        self.filename = filename
        self._read()

    def set_block_size(self, size):
        '''
        Set the block size value without recomputing blocks
        '''
        self.size = int(size)
        self._write()

    def update_block_size(self, size):
        '''
        Recompute blocks based on new size
        '''
        if self.size == size:
            return

        newblocks = []
        count = 0
        total = 0
        offset = None
        
        for value in self.blocks:
            value = int(value)
            if value == count:
                if offset == None:
                    offset = count
                total += self.size
            elif offset != None:
                start = ((offset * self.size) / size) + 1
                newblocks.extend(range(start, start + (total / size)))
                total = 0
                offset = None
            count += 1

        if offset != None:
            start = ((offset * self.size) / size) + 1
            newblocks.extend(range(start, start + (total / size)))

        self.blocks = newblocks
        self.set_block_size(size)

    def start_byte(self):
        '''
        Returns byte to start at, all previous are OK
        '''
        if len(self.blocks) == 0:
            return 0
        
        count = 0
        for value in self.blocks:
            if int(value) != count:
                return (count + 1) * self.size
            count += 1
            
        return None

    def add_block(self, block_id):
        '''
        Add a block to list of completed
        '''
        if str(block_id) not in self.blocks:
            self.blocks.append(str(block_id))
        self._write()
        
    def remove_block(self, block_id):
        '''
        Remove a block from list of completed
        '''
        self.blocks.remove(str(block_id))
        self._write()
        
    def clear_blocks(self):
        '''
        Remove all blocks from completed list
        '''
        self.blocks = []
        self._write()

    def extend_blocks(self, blocks):
        '''
        Replace the list of block ids
        '''
        for block in blocks:
            if str(block) not in self.blocks:
                self.blocks.append(str(block))
        self._write()

    def _write(self):
        filehandle = open(self.filename, "w")
        filehandle.write("%s:" % str(self.size))
        #for block_id in self.blocks:
            #filehandle.write(str(block_id) + ",")
        filehandle.write(",".join(self.blocks))
        filehandle.close()

    def _read(self):
        try:
            filehandle = open(self.filename, "r")
            resumestr = filehandle.readline()
            (size, blocks) = resumestr.split(":")
            self.blocks = blocks.split(",")
            self.size = int(size)
            filehandle.close()
        except IOError:
            pass

    def complete(self):
        '''
        Download completed, remove block count file
        '''
        os.remove(self.filename)

def verify_chunk_checksum(chunkstring, checksums={}):
    '''
    Verify the checksum of a file
    First parameter, filename
    Second parameter, optional, expected dictionary of checksums
    Returns True if first checksum provided is valid
    Returns True if no checksums are provided
    Returns False otherwise
    '''

    try:
        checksums["sha512"]
        if hashlib.sha512(chunkstring).hexdigest() == checksums["sha512"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha384"]
        if hashlib.sha384(chunkstring).hexdigest() == checksums["sha384"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha256"]
        if hashlib.sha256(chunkstring).hexdigest() == checksums["sha256"].lower():
            return True
        else:
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha1"]
        if hashlib.sha1(chunkstring).hexdigest() == checksums["sha1"].lower():
            return True
        else:
            return False
    except KeyError: pass
    try:
        checksums["md5"]
        if hashlib.md5(chunkstring).hexdigest() == checksums["md5"].lower():
            return True
        else:
            return False
    except KeyError: pass
    
    # No checksum provided, assume OK
    return True

def verify_checksum(local_file, checksums={}):
    '''
    Verify the checksum of a file
    First parameter, filename
    Second parameter, optional, expected dictionary of checksums
    Returns True if first checksum provided is valid
    Returns True if no checksums are provided
    Returns False otherwise
    '''
    
    try:
        checksums["sha512"]
        if filehash(local_file, hashlib.sha512()) == checksums["sha512"].lower():
            return True
        else:
            #print "\nERROR: sha512 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha384"]
        if filehash(local_file, hashlib.sha384()) == checksums["sha384"].lower():
            return True
        else:
            #print "\nERROR: sha384 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha256"]
        if filehash(local_file, hashlib.sha256()) == checksums["sha256"].lower():
            return True
        else:
            #print "\nERROR: sha256 checksum failed for %s." % os.path.basename(local_file)
            return False
    except (KeyError, AttributeError): pass
    try:
        checksums["sha1"]
        if filehash(local_file, hashlib.sha1()) == checksums["sha1"].lower():
            return True
        else:
            #print "\nERROR: sha1 checksum failed for %s." % os.path.basename(local_file)
            return False
    except KeyError: pass
    try:
        checksums["md5"]
        if filehash(local_file, hashlib.md5()) == checksums["md5"].lower():
            return True
        else:
            #print "\nERROR: md5 checksum failed for %s." % os.path.basename(local_file)
            return False
    except KeyError: pass
    
    # No checksum provided, assume OK
    return True

def remote_or_local(name):
    '''
    Returns if the file path is a remote file or a local file
    First parameter, file path
    Returns "REMOTE" or "LOCAL" based on the file path
    '''
    #transport = urlparse.urlsplit(name).scheme
    transport = get_transport(name)
        
    if transport != "":
        return "REMOTE"
    return "LOCAL"

def get_transport(url):
    '''
    Gets transport type.  This is more accurate than the urlparse module which
    just does a split on colon.
    First parameter, url
    Returns the transport type
    '''
    url = str(url)
    result = url.split("://", 1)
    if len(result) == 1:
        transport = ""
    else:
        transport = result[0]
    return transport

def filehash(thisfile, filesha):
    '''
    First parameter, filename
    Returns SHA1 sum as a string of hex digits
    '''
    try:
        filehandle = open(thisfile, "rb")
    except:
        return ""

    data = filehandle.read()
    while(data != ""):
        filesha.update(data)
        data = filehandle.read()

    filehandle.close()
    return filesha.hexdigest()

def path_join(first, second):
    '''
    A function that is called to join two paths, can be URLs or filesystem paths
    Parameters, two paths to be joined
    Returns new URL or filesystem path
    '''
    if first == "":
        return second
    if remote_or_local(second) == "REMOTE":
        return second

    if remote_or_local(first) == "REMOTE":
        if remote_or_local(second) == "LOCAL":
            return urlparse.urljoin(first, second)
        return second

    return os.path.normpath(os.path.join(first, second))

def start_sort(urldict):
    urls = copy.deepcopy(urldict)
    localurls = {}
    if COUNTRY != None:
        for url in urls.keys():
            if COUNTRY.lower() == urls[url].location.lower():
                localurls[url] = urls[url]
                urls.pop(url)

    newurls = sort_prefs(localurls)
    newurls.extend(sort_prefs(urls))
    #for i in range(len(newurls)):
    #    print i, newurls[i]
    return newurls

def sort_prefs(mydict):
    newurls = []

    for url in mydict.keys():
        newurls.append((mydict[url].preference, mydict[url].url))

    newurls.sort()
    newurls.reverse()
    
    result = []
    for url in newurls:
        result.append(url[1])
    return result
