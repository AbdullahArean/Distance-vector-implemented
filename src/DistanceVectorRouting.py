import time
import sys
import os
import threading
from socket import *
import math
SUSPEND_TIMEOUT = 3
class possible_path:
    def __init__(self, dis, nxthop):
        self.dis = dis
        self.nxthop = nxthop

    def equals(self, path2):
        return self.dis == path2.dis and self.nxthop == path2.nxthop  

class adjacent_node:
    def __init__(self, linkCost, port, timeout):
        self.linkCost = linkCost
        self.port = port
        self.timeout = timeout
        self.paths = dict()

router_id = str()
router_port = int()
router_filename = str()
router_neighbours = dict()
router_routes = dict()

lockthread = threading.Lock()

def pkt_send_creation(dest_id, cost):
    distvector = str(router_id)

    if cost: 
        distvector += ' ' + str(router_neighbours[dest_id].linkCost)
    distvector += '\n'

    for id, path in router_routes.items():
        if path.nxthop == dest_id:
            distvector += str(id) + " " + str(math.inf) + '\n'
        else:
            distvector += str(id) + " " + str(path.dis) + '\n'

    return bytes(distvector, 'utf-8')


def distancevectorshare(cost):
    sendSocket = socket(AF_INET, SOCK_DGRAM)
    lockthread.acquire()
    for id, neighbour in router_neighbours.items():
        sendSocket.sendto(pkt_send_creation(id, cost), ('localhost', neighbour.port))
    lockthread.release()
    sendSocket.close()

def printdistancetable():
    string = '\t'

    for id in sorted(router_routes.keys()): 
        string += '\t' + id
    print(string)

    string = router_id + '\t'
    for id in sorted(router_routes.keys()):
        string += '\t' + str("%.1f" % router_routes[id].dis)
    print(string)

    for id in sorted(router_neighbours.keys()):
        string = id+'\t'+str(router_neighbours[id].linkCost)
        for key2 in sorted(router_neighbours[id].paths.keys()):
            string += '\t' + str("%.1f" % router_neighbours[id].paths[key2].dis)
        print(string)
    print('')

def checktimeout():
    while 1:
        time.sleep(1)
        for id, neighbour in router_neighbours.items():
            s = socket(AF_INET, SOCK_DGRAM)
            try:
                s.bind(('localhost', neighbour.port))
                s.close()
                if router_neighbours[id].linkCost != math.inf:
                    lockthread.acquire()

                    router_routes[id].dis = math.inf
                    neighbour.linkCost = math.inf 
                    neighbour.timeout = time.time()
                    for key2, item2 in router_routes.items():
                        if item2.nxthop == id:
                            item2.dis = math.inf

                    lockthread.release()
                    distancevectorshare(False)
                    threading.Timer(SUSPEND_TIMEOUT, target=distancevectoralgorithm).start()
            except:
                pass

def threadlisten():
    socketlisten = socket(AF_INET, SOCK_DGRAM)
    socketlisten.bind(('localhost', router_port))
    while 1:
        message, socketAddress = socketlisten.recvfrom(2048)

        lines = str(message)[2:len(str(message))-1].split('\\n')
        firstLine = lines[0].split()
        source = firstLine[0]

        router_neighbours[source].timeout = -1.0

        if len(firstLine) > 1:
            router_neighbours[source].linkCost = float(firstLine[1])
            router_neighbours[source].timeout = -1

        lockthread.acquire()
        for i in range(1, len(lines)):
            if lines[i] == '':
                continue
            tokens = lines[i].split()
            newPath = possible_path(float(tokens[1]),'direct')
            if tokens[0] not in router_neighbours[source].paths:
                newNode(tokens[0])
            if not router_neighbours[source].paths[tokens[0]].equals(newPath):
                router_neighbours[source].paths[tokens[0]] = newPath
        threading.Thread(target=distancevectoralgorithm).start()
        lockthread.release()


def newNode(name):
    global router_neighbours
    p = possible_path(math.inf, 'direct')
    router_routes[name] = p
    for id, neighbour in router_neighbours.items():
        neighbour.paths[name] = p


def distancevectoralgorithm():
    global router_routes

    isChanged = False

    lockthread.acquire()
    for id, route in router_routes.items():
        m_list = list()
        if id == router_id:
            continue
        if id in router_neighbours:
            if time.time() > router_neighbours[id].timeout and time.time() < router_neighbours[id].timeout + SUSPEND_TIMEOUT:
                router_routes[id] = possible_path(math.inf, 'direct')
                continue
            else:
                m_list.append(possible_path(router_neighbours[id].linkCost, 'direct'))

        for id2, neighbour in router_neighbours.items():
            p = possible_path(router_neighbours[id2].linkCost + neighbour.paths[id].dis, id2)
            m_list.append(p)
        m_list.append(p)
        m = min(m_list, key = lambda x: x.dis)
        if not router_routes[id].equals(possible_path(m.dis,m.nxthop)):
            router_routes[id] = possible_path(m.dis,m.nxthop)
            isChanged = True

    lockthread.release()
    if isChanged:
        distancevectorshare(False)


def UserPrompt():
    option = 0
    while(1):
        print('\n****ROUTER ' + router_id + '****\n')

        option = int(input('1: Display Costs of Reaching Other Routers.\n2: Display Distance Vector Table of The Router.\n3: Edit Cost of Link with adjacent_node.\n4: Exit\nPlease Enter Your Choice:(1/2/3/4): '))
        if option == 1:
            print('Destination\tNext Hop\tDistance')
            for id, route in sorted(router_routes.items()):
                if id != router_id:
                    print('     ' + id + '\t\t' + route.nxthop + '\t\t' + str("%.1f" % route.dis))
        elif option == 2:
            printdistancetable()
        elif option == 3:
            string = 'Neighbours:'
            for id in sorted(router_neighbours.keys()):
                string += ' ' + id
            print(string)
            toEdit = input('Enter which link to edit: ')
            newDistance = float(input('Enter new dis for ' + toEdit + ': '))
            router_neighbours[toEdit].linkCost = newDistance

            sendSocket = socket(AF_INET, SOCK_DGRAM)
            lockthread.acquire()
            sendSocket.sendto(pkt_send_creation(toEdit, True), ('localhost', router_neighbours[toEdit].port))
            lockthread.release()
            sendSocket.close()

            threading.Thread(target=distancevectoralgorithm).start()

        elif option == 4:
            os._exit(-1)
        else :
            continue;

if __name__ == '__main__':  #starting point
    try:
        router_filename = sys.argv[1]
        with open(router_filename, 'r') as f:
            first_line = f.readline()
            router_id, router_port = first_line.split()
            router_port = int(router_port)
    except ValueError or IndexError:
        print('Incorrect command-line arguments.\npython DVR.py <ID> <port> <filename>')
        exit(0)

    print("Router "+router_id)

    router_routes[router_id] = possible_path(0, 'direct')

    file = open(router_filename)
    lines = file.readlines()
    for i in range(2, len(lines)):
        tokens = lines[i].split()
        router_neighbours[tokens[0]] = adjacent_node(float(tokens[1]), int(tokens[2]), -1)
        router_routes[tokens[0]] = possible_path(float(tokens[1]), 'direct')
    for id, neighbour in router_neighbours.items():  
        p = possible_path(math.inf, 'direct')
        for id2, neighbour2 in router_neighbours.items():
            neighbour.paths[id2] = p
        neighbour.paths[router_id] = possible_path(0, 'direct')

    threading.Thread(target=distancevectorshare, kwargs={'cost': True}).start()  #temporary thread for seding DV
    threading.Thread(target=threadlisten).start()
    threading.Thread(target=UserPrompt).start()
    threading.Thread(target=checktimeout).start()
