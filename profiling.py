# A scope based class that gets the amount of time something took to execute
import time

DO_FUNCTION_PROFILING = False
DO_SCOPE_PROFILING = False

if DO_FUNCTION_PROFILING:

    class Timer:
        def __init__(self, name : str):
            self.mName = name
            self.mStartTime = time.perf_counter() * 1000.0 # Get milliseconds

            print("%s Starting..." %self.mName)

        def __del__(self):
            endTime = time.perf_counter() * 1000.0 # Get Milliseconds

            duration = endTime - self.mStartTime

            print("%s took %sms" %(self.mName, duration))

else:

    class Timer:
        def __init__(self, dummyParam):
            """
            DO nothing!
            We don't always want profiling and optimizations will delete this
            """

if DO_SCOPE_PROFILING:
    class ScopeTimer:
        def __init__(self, name : str):
            self.mName = name
            self.mStartTime = time.perf_counter() * 1000.0 # Get milliseconds

            print("%s Scope Starting..." %self.mName)

        def __del__(self):
            endTime = time.perf_counter() * 1000.0 # Get Milliseconds

            duration = endTime - self.mStartTime

            print("%s took %sms" %(self.mName, duration))

else:
    class ScopeTimer:
        def __init__(self, dummyParam):
            """
            DO nothing!
            We don't always want profiling and optimizations will delete this
            """