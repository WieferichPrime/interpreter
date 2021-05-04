class Elem:
    def __init__ (self,value = None):
        self.value = value
        self.nextelem = None

class LinkedList:
    def __init__(self , *elems):
        self.head = None
        for elem in elems[0]:
            self.push(elem)

    def __repr__(self):
        current = self.head
        str = '[ '
        while current is not None:
            str += f'{current.value},'
            current = current.nextelem
        str += ']'
        return str


    def contains(self, value):
        lastelem = self.head
        while (lastelem):
            if value == lastelem.value:
                return True
            else:
                lastelem = lastelem.nextelem;
        return False

    def push(self, value):
        newelem = Elem(value)
        if self.head is None:
            self.head = newelem
            return
        lastelem = self.head
        while (lastelem.nextelem):
            lastelem = lastelem.nextelem
        lastelem.nextelem = newelem

    def get(self, index):
        lastelem = self.head
        elemIndex = 0
        while elemIndex <= index:
            if elemIndex == index:
                return lastelem.value
            elemIndex = elemIndex + 1
            lastelem = lastelem.nextelem

    def remove(self, value):
        current = self.head
        if current is not None:
            if current.value == value:
                self.head = current.nextelem
                return
        while current is not None:
            if current.value == value:
                break
            last = current
            current = current.nextelem
        if current == None:
            return
        last.nextelem = current.nextelem

    def printList(self):
        current = self.head
        while current is not None:
            print(current.value,end=' ')
            current = current.nextelem