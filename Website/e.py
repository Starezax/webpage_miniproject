class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

head = Node(4)

new_head = Node(2)
new_head.next = head
head = new_head

current = head
while current.next:
    current = current.next
current.next = Node(8)

node_10 = Node(10)
node_10.next = current.next
current.next = node_10

current = head
while current:
    print(current.data, end=",")
    current = current.next
print("None")
