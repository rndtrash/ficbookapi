import time

# Класс для высчитывания времени совершения запроса
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()
         
    def __exit__(self, type, value, traceback):
        print ("Elapsed time: {:.3f} sec".format(time.time() - self._startTime))