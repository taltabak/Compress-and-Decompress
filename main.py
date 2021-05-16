import bitarray
import sys

#----------------------------------------Classes---------------------------------#
class Node:                                             #represent a node in the Huffman tree

    def __init__(self,freq,leaf):                       #node constructor
        self.freq = freq
        self.leaf = leaf

    def insert(self, leftSon , rightSon):               #assign left and right children
        self.leftSon = leftSon
        self.rightSon= rightSon

    def setValue(self,value):
        self.value = value

class Tree:                                             #represent the Huffman tree
    root = None
    treeDictionary = {}                                 #map the codes by chars (Compression)
    mapLeavesString = []                                #list of 0's and 1's which includes all of the leaves and later the encoded data (Decompression)
    treeEncoding = []                                   #list of 0's and 1's which includes the encoded tree (Decompression)
    leavesEncoding = []                                 #list of the leaves we wish to encode (Compression)

    def constructHuffmanTree(self,vector):              #generates an Huffman tree by vector of frequencies (Compression)
        if len(vector) == 1:
            one_node = Node(vector[0][1],True)
            one_node.setValue(vector[0][0])
            second_node = Node(0,True)
            second_node.setValue(" ")
            new_root = Node(0,False)
            new_root.insert(one_node,second_node)
            vector.remove(vector[0])
            vector.append((new_root,new_root.freq,True))
        while len(vector) > 1:
            m1, m2 = ( "",float('inf'), ""), ( "",float('inf'), "")
            for tuple in vector:
                if tuple[1] < m1[1]:
                    m2 = m1
                    m1 = tuple
                elif tuple[1] < m2[1]:
                    m2 = tuple
            if m1[2] == True:
                letter = m1[0]
                leaf1 = Node(m1[1],True)
                leaf1.setValue(letter)
            else:
                leaf1 = m1[0]
            if m2[2] == True:
                letter = m2[0]
                leaf2 = Node(m2[1],True)
                leaf2.setValue(letter)
            else:
                leaf2 = m2[0]
            new_node = Node(m1[1]+m2[1],False)
            new_node.insert(leaf1,leaf2)
            vector.append((new_node,new_node.freq,False))
            vector.remove(m1)
            vector.remove(m2)
        self.root = vector[0][0]

    def generateDictionary(self,node,code):             #walks through the tree in order to map Huffman code of each character (Compression)
        if(node.leaf == True):
            self.treeDictionary[node.value] = code
        else:
            self.generateDictionary(node.leftSon,code+"0")
            self.generateDictionary(node.rightSon,code+"1")

    def first_index(self,string):                       #gets the first index where there is more '1' than '0' in a string (used in the next function) (Decompression)
        index = 0
        for i in range(len(string)):
            if string[i] == '0':
                index = index+1
            if string[i] == '1':
                index = index-1
            if index < 0:
                return i

    def recExtractTree(self,treeString):                #recursive function which gets the encoded tree and constructs an actual object of the tree (Decompression)
        if len(treeString) == 0:
            return
        if treeString[0] == '1':
            leafValue = self.mapLeavesString[:8]
            leafValue = ''.join(leafValue)
            n = int(leafValue, 2)
            node1 = Node(0,True)
            node1.setValue(n.to_bytes((n.bit_length() + 7) // 8, 'big').decode())
            self.mapLeavesString = self.mapLeavesString[8:]
            return node1
        j = self.first_index(treeString)
        node2 = Node(0,False)
        if treeString[1] == '1' and treeString[2] == '1':
            l = ['1']
            r = ['1']
        else:
            if len(treeString) == j+1:
                j = self.first_index(treeString[1:])
            l = treeString[1:j+2]
            r = treeString[j+2:]
        node2.leftSon = self.recExtractTree(l)
        node2.rightSon = self.recExtractTree(r)
        return node2

    def extractTree(self,string):                       #the call of the recursive function which construct the tree from the string  (Decompression)
        j = self.first_index(string)
        treeString = string[:j+1]
        self.mapLeavesString = string[j+1:]
        self.root = self.recExtractTree(treeString)

    def encodeTree(self,node):                          #the function runs a preorder encoding of the tree leaf = '1', otherwise '0' (Compression)
        if node.leaf == True:
            self.treeEncoding.append('1')
            self.leavesEncoding.append(format(ord(node.value), '08b'))
        else:
            self.treeEncoding.append('0')
            self.encodeTree(node.leftSon)
            self.encodeTree(node.rightSon)

    def walktree(self,node,index):                      #walks through the encoded tree by the code in order to find the correct leaf (Decompression)
        if node.leaf == True:
            return (node.value,index)
        elif self.mapLeavesString[index] == '0':
            return self.walktree(node.leftSon,index+1)
        elif self.mapLeavesString[index] == '1':
            return self.walktree(node.rightSon,index+1)

    def writeTxt(self):                                 #for all the string of 0's and 1's the function finds out the text (Decompression)
        index = 0
        txtString = ""
        while index < len(self.mapLeavesString):
            tuple = self.walktree(self.root,index)
            txtString = txtString + tuple[0]
            index = tuple[1]
        return txtString

############################################### END OF CLASSES #################################

def calculateFreq(txtFile):                             #calculate frequencies of chars in a given string
    freqDictionary = {}
    freqlist = []
    for char in txtFile:
        if char in freqDictionary:
            freqDictionary[char] = freqDictionary[char]+1
        else:
            freqDictionary[char] = 1
    freqlist = [(char,prob,True) for char, prob in freqDictionary.items()]
    return freqlist

def compress(txtFileName , cmpFileName):                #compress a file by a name of the file
    f = open(txtFileName,'r')
    txtFile = f.read()
    f.close()
    freqlist = calculateFreq(txtFile)
    tree = Tree()
    tree.constructHuffmanTree(freqlist)
    tree.generateDictionary(tree.root,"")
    tree.encodeTree(tree.root)
    encoding = ''.join(tree.treeEncoding) + ''.join(tree.leavesEncoding)
    for char in txtFile:
        encoding = encoding+tree.treeDictionary[char]
    n = len(encoding)%8
    for i in range(8-n):
        encoding = '1' + encoding
    bitsEncoding = bitarray.bitarray(encoding)
    fh = open(cmpFileName, 'wb')
    bitsEncoding.tofile(fh)
    fh.close()

def decompress(cmpFileName , txtFileName):              #decompress a file by a name of the file
    f = open(cmpFileName,'rb')
    cmpFile = bitarray.bitarray()
    cmpFile.fromfile(f)
    f.close()
    binString = cmpFile.to01()
    i = 0
    for bin in binString:
        if bin == '0':
            break
        i = i+1
    binString = binString[i:]
    tree = Tree()
    tree.extractTree(binString)
    txt = tree.writeTxt()
    fh = open(txtFileName, 'w')
    fh.write(txt)
    fh.close()

#############MAIN######################

print("Welcome to the Huffman code exractor by Tal.")
while 1 == 1:
    method=input("\nPlease select what action do you want to perform:\nto compress enter 'C' |||| to decompress enter 'D'\n")
    if method == 'C':
        txtfilename = input("Please Type the name of the file you wish to compress (there is no need to type the file extension):\n")
        cmpfilename = txtfilename + ".cmp"
        txtfilename = txtfilename + ".txt"
        compress(txtfilename, cmpfilename)
        print("Compression successfully completed\n")
    elif method == 'D':
        cmpfilename  = input("Please Type the name of the file you wish to decompress (there is no need to type the file extension):\n")
        txtfilename = cmpfilename  + ".txt"
        cmpfilename = cmpfilename + ".cmp"
        decompress(cmpfilename,txtfilename)
        print("Decompression successfully completed\n")
    else:
        print("Please type 'C' or 'D'")
        continue
    question = input("Do you wish to perform another action?\ny/n\n")
    if question == 'n':
        print("Bye")
        break
