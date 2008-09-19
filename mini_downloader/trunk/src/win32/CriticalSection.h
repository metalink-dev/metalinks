#ifndef CRITICALSECTION_H
#define CRITICALSECTION_H

#include <windows.h>

class CriticalSection
{
public:
    CriticalSection()
    {
        InitializeCriticalSection(&_csection);
    }
    
    ~CriticalSection()
    {
        DeleteCriticalSection(&_csection);
    }
    
    void enter()
    {
        EnterCriticalSection(&_csection);
    }
    
    void leave()
    {
        LeaveCriticalSection(&_csection);
    }
    
    class Lock;
    class MultiLock;
private:
    CRITICAL_SECTION _csection;
};

class CriticalSection::Lock
{
public:
    Lock(CriticalSection& csection) : _csection(csection)
    {
        _csection.enter();
    }
    ~Lock()
    {
        _csection.leave();
    }
private:
    CriticalSection& _csection;
};

class CriticalSection::MultiLock
{
public:
    MultiLock(CriticalSection& csection, bool enter_now = false) : _csection(csection)
    {
        _num_entered = 0;
        if(enter_now) enter();
    }
    ~MultiLock()
    {
        leave_all();
    }
    // Can be called several times, but not infitely many...
    void enter()
    {
        _csection.enter();
        _num_entered++;
    }
    // Can be called even when enter( ) has not been called
    void leave()
    {
        if(_num_entered > 0) {
            _num_entered--;
            _csection.leave();
        }
    }
    // Can be called even when enter( ) has not been called
    void leave_all()
    {
        while(_num_entered > 0)
        {
            _num_entered--;
            _csection.leave();
        }
    }
private:
    CriticalSection& _csection;
    unsigned int _num_entered;
};

#endif
