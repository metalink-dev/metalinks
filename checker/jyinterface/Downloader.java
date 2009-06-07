package jyinterface;

public interface Downloader {
    public void start(String url, String path);
    public Download[] get_managers();
}