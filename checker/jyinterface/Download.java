package jyinterface;

import java.util.Observer;

public interface Download {
    public static final int DOWNLOADING = 0;
    public static final int PAUSED = 1;
    public static final int COMPLETE = 2;
    public static final int CANCELLED = 3;
    public static final int ERROR = 4;
    public static final String STATUSES[] = {"Downloading", "Paused", "Complete", "Cancelled", "Error"};
    public void start(String url, String path);
    public int getSize();
    public float getProgress();
    public int getStatus();
    public void pause();
    public void resume();
    public void cancel();
    public String displayFileName();
    public void addObserver(Observer o);
    public void deleteObserver(Observer o);
}