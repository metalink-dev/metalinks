# encoding: utf-8
import unittest

b64_metalink = "QlpoOTFBWSZTWXyucbcAAqXfnFUSUQf//4uHToA/79/wBgABAAgAUAW+uzboE"
b64_metalink += "3e9urbI0ADhqp+KaYRoSeGptRDag0MRkAGQAIqn40GJKftJpQ0GgAAwmIAAC"
b64_metalink += "KeATQmJUAaaAyaAAAAAGmikA0ABoAAAAAAD1BJECaCaZAJo0JlNPKeo2k8p6"
b64_metalink += "jTTT0ygmLJkAqAgOIIB0IEWCAPQdI8+/x8vr8pUREmfc5SzPElgJbJRiAUg7"
b64_metalink += "2+PmJWE0bpKEdz8I4huDc/FsAbFz9jvc0CfNBpzr0eGnQSxRYUmsGwctw4Dk"
b64_metalink += "WOxtF30nYjhPus0MixMzEKf7zKhNffi0fWXrCJ084HqfIOgZ2yYEVZE4ugzZ"
b64_metalink += "DsEZTPtFA4ZLPqZ0u7nG+N+3Pm5DieE+gKElpsI1jjURGyiaekKP3sfU9Tjm"
b64_metalink += "RxnolVlkuNCRlfW2C75InBVG1sge4kZh0s6Y915ko5vFgXTalY2eBOMcKETb"
b64_metalink += "LLCBrTXZQHGxYzQYUqJimQ4xcGat8qd8JimM3pL2KUBzXajYA3SMWcaOr21P"
b64_metalink += "DmNVcncYkQ3u1MnLJw6jZrur5cgrhwxdbsGhohYJaoVYHDREtC6qiWnJQGGV"
b64_metalink += "01aD0tG0Ndpyd6Ru9JxYlOsuzOmpMSV4OkPl9DAIOr3zS28XGipqsrm9sxDv"
b64_metalink += "SRYDGcmd3C6tmw7wYEh1wo5qjHFYWTSlhDT5RjzTGskpIFqvrZLyM644e4Ex"
b64_metalink += "XyLbgRIuvhCj3fT7c0rlkE75hMxA7PdbBwySjTJjCvlghJIgYxtrTrrVajWA"
b64_metalink += "k3m90XTiqgsoVWRGJgZPRSO/RiAyZSHZF0HUCu1EgVtmOq1GKGkb9tOGzp9e"
b64_metalink += "isqu5rbdMNE95d23DvPI63V3BvMQaCMGZjJpRGd4uMyZgoYlWMewdBQBdasU"
b64_metalink += "YgTyFLFKNZ4NCKTA02I9fRoJGFhHzEHZqgnBTKCewABGCki0RHP3sCgKgImY"
b64_metalink += "PnffKyYzD2URB3GYvncpEezw2mbJvtKH1PSSAb9h6ZsIDRfqz8pczNfP1apd"
b64_metalink += "SmdbtZY2OW2WeQ8bnUsJ7nFOejtJl07p1v8zkkdaD6frzG5dZpBwEbws3LPy"
b64_metalink += "V8KccJkjBRFCyORiEL5cjeC+hHtJek65V0zUzrlVlSel4o4AAm75sV7Dl78Y"
b64_metalink += "zXgRzIrm1b0hpsbmcxeUe67r2/c1Y5VvMKiDosFugzTww2GjHx/C7yR0qMe5"
b64_metalink += "Bep7Ndt8xZF1EKxmM6oXFF71iEpgOoi+e5oMNGLOLRaFzV0Uxyq3QuwwIEUc"
b64_metalink += "phCIgl9kCnjVdeaRkiDja66Sx8iwW2bFlbbsczFIO9GuLL3/ONnbMnteCpEK"
b64_metalink += "TplrKhrwg+rHkCOCfWV19OYWfw3YpvZBGS19kPhHPcLit24XI9/FnFs6IGhk"
b64_metalink += "tRaNc7M1RaD2oB7YImxl+KkuNuXDtdfkVD4ks9cUpRYHZplVjl79KoB+Dtsh"
b64_metalink += "Wii3NElUjuHx5YeHcEW7uJyHNg6sqt8lTtKBRcOSEMwkffSYAiwEdJMmA7Kv"
b64_metalink += "YpX/MzQzG86heeooYFoI1o9iwR8Cnv03Cv05jDJmZmGRaL42UoA/fDcUFYOK"
b64_metalink += "wu0NVoAadPMibByDB0xGTMcwuoBqyopE+dEVueiCcpE99o8fDIawo1aantYS"
b64_metalink += "lUKhEpTJQxhFQY+RAVRZyQQZLiEOhhMjZIAdMuTmRmY471YZb6CNsvRLItoI"
b64_metalink += "K242SloFLqIFIM2YZpMwVGtNK1zKEmehAwUxUEQEXMzbWObcDq+rO7lpdEXD"
b64_metalink += "TRG8Mh74AIkOBBXJVrlakSee3Wy4MYu82IxZqlSopF6NuE0OX8dWjPM2lrMM"
b64_metalink += "tiyFkUlcIxgREMK9ECdpVBEw05DDoZadRCEk45sD+o0IBINt+lMuqjnD8tSF"
b64_metalink += "ik4OR0V38XckU4UJB8rnG3A"

class TestMetalinkLoading(unittest.TestCase):
  
  def test_load_data(self):
    import metalink
    import base64
    import bz2
    ml_data = base64.b64decode(b64_metalink)
    ml_data = bz2.decompress(ml_data)
    ml = metalink.parse_string(ml_data)
    self.assertEqual(ml.identity, u'Test identity')
    self.assertEqual(ml.version, u'1.0.0')
    self.assertEqual(ml.description, u'This is my description, with an & in it and some Swedish letters: åäö.')
    self.assertEqual(ml.releasedate, u'2008-01-05')
    self.assertEqual(ml.tags, u'example, metalink, unittest')
    self.assertEqual(ml.publisher_name, u'The publisher')
    self.assertEqual(ml.publisher_url, u'http://www.the-publisher.com/')
    self.assertEqual(ml.license_name, u'GNU GPL')
    self.assertEqual(ml.license_url, u'http://www.gnu.org/licenses/gpl.html')
    self.assertEqual(len(ml.files), 1)
    file = ml.files[0]
    self.assertEqual(file.identity, u'File identity')
    self.assertEqual(file.version, u'1.1.0')
    self.assertEqual(file.size, 4512266)
    self.assertEqual(file.description, u'File description.')
    self.assertEqual(file.copyright, u'Copyright statement')
    self.assertEqual(file.changelog, u'Changelog text...')
    self.assertEqual(file.logo, u'http://test.com/logo.png')
    self.assertEqual(file.tags, u'file, metalink, unittest')
    self.assertEqual(file.language, u'en-US')
    self.assertEqual(file.os, u'Windows-x86')
    self.assertEqual(file.mimetype, u'text/html')
    self.assertEqual(file.releasedate, u'2007-10-23')
    self.assertEqual(file.upgrade, u'install')
    self.assertEqual(file.screenshot, u'http://test.com/screenshot.php?id=87')
    self.assertEqual(file.publisher_name, u'The file publisher')
    self.assertEqual(file.publisher_url, u'http://www.the-file-publisher.com/')
    self.assertEqual(file.license_name, u'My own license')
    self.assertEqual(file.license_url, u'')
    self.assertEqual(file.maxconnections, 7)
    self.assertEqual(len(file.urls), 2)
    self.assertEqual(file.urls[0].url, u'http://file-server.com/files/test-1.0.0.exe')
    self.assertEqual(file.urls[0].location, u'')
    self.assertEqual(file.urls[0].preference, -1)
    self.assertEqual(file.urls[0].maxconnections, 2)
    self.assertEqual(file.urls[1].url, u'http://file-server.se/pub/test/test-1.0.0.exe')
    self.assertEqual(file.urls[1].location, u'se')
    self.assertEqual(file.urls[1].preference, 97)
    self.assertEqual(file.urls[1].maxconnections, 1)
    self.assertEqual(file.hashes[0].type, u'md5')
    self.assertEqual(file.hashes[0].hash, u'1798e7aa4bf190563c6c680a2bd6599e')
    self.assertEqual(file.hashes[1].type, u'sha1')
    self.assertEqual(file.hashes[1].hash, u'fa721e4157b25de49fca263af7e4b0a866118e51')
    self.assertEqual(file.piece_type, u'sha1')
    self.assertEqual(file.piece_length, 262144)
    self.assertEqual(file.piece_hashes[0], u'c9e34e616c69715020eadd58e58aab14352f2426')
    self.assertEqual(file.piece_hashes[16], u'4444bc23698ec235cbcc1906092793e7c8ef5863')
    self.assertEqual(file.piece_hashes[17], u'90fc9469cff5493bfc421c7bf268ee6fbbed5086')
  
  def test_load_empty(self):
    import metalink
    self.assertRaises(metalink.MetalinkException, metalink.parse_string, "")

def run_tests():
  unittest.main()

if __name__ == '__main__':
  run_tests()