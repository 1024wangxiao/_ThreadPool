#  _*_ encoding=utf-8 _*_
import threading
import time
class ThreadSafeQueueException(Exception):
    pass
#线程安全的队列
class ThreadSafeQueue(object):
    def __init__(self,max_size=0):
        self.queue=[]
        self.max_size=max_size
        #互斥量
        self.lock=threading.Lock()
        #条件变量
        self.condition=threading.Condition()
    #当前队列的数量
    def size(self):
        #由于可能会被多线程的调用，所以我们在获取之前要进行加锁
        self.lock.acquire()
        size=len(self.queue)
        self.lock.release()
        return size

    #放队列里面放入元素
    def put(self,item):
        if self.max_size!=0 and self.size()>self.max_size:
            return ThreadSafeQueueException()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        #条件变量的作用就是，有可能这时候队列空了，
        # 然后有其他线程在进行取操作，线程阻塞，那么我们添加完成之后可以发出唤醒
        self.condition.acquire()
        self.condition.notify()
        self.condition.release()
        pass
    def batch_put(self,item_list):
        if not isinstance(item_list,list):
            item_list=list(item_list)
        for item in item_list:
            self.put(item)
    #从队列取取出元素
    #block参数表示当前队列没有元素的时候是否阻塞等待，timeout是等待的时间
    def pop(self,block=False,timeout=0):
        if self.size()==0:
            #需要阻塞等待
            if block:
                self.condition.acquire()
                self.condition.wait(timeout=timeout)
                self.condition.release()
            else:
                return None

        self.lock.acquire()
        item=None
        if len(self.queue)>0:
            item = self.queue.pop()
        self.lock.release()
        return item
    def get(self,index):
        self.lock.acquire()
        item=self.queue[index]
        self.lock.release()
        return item

if __name__=="__main__":
    queue =ThreadSafeQueue(max_size=100)
    def produce():
        while True:
            queue.put(1)
            time.sleep(3)
    def consumer():
        while True:
            item=queue.pop(block=True,timeout=2)
            print("get item from queue %d"%item)
            time.sleep(1)
    thread1=threading.Thread(target=produce)
    thread2=threading.Thread(target=consumer)
    thread1.start()
    thread2.start()
    thread1.join()#join方法可以将线程阻塞在这里，只有将所有join线程完成之后才会执行下面的线程
                    # 除此之外， 线程的整个运行时间是取这里的最大值
    thread2.join()