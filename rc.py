

from functools import cache
from math import sqrt,exp,log
import os
from tkinter import W 

def XORstrings(a,b):
    xor = int(a, 2) ^ int(b, 2)
    return bin(xor)[2:].zfill(len(a))

@cache
def Expand(bit_string, length):
    output = bit_string
    output = ''.join([output[:2],output[2:].zfill(length)])  
    return output

@cache
def Shift(number, w, bits, side):
    bin_string = Expand(bin(number), w)
    bits %= w										# поворот 
    bin_string = bin_string[2:]
    if side == 'left':  return int('0b' + bin_string[bits:] + bin_string[:bits], 2)
    if side == 'right': return int('0b' + bin_string[-bits:] + bin_string[:-bits], 2)

def bytesToBin(bytes_string):
		output = bytes_string
		output = [Expand(bin(char),8)[2:] for char in output]        # байты в биты   
		output = ''.join(output)
		return output

def binToBytes(bin_string):
		output = [int('0b' + bin_string[block * 8 : (block + 1) * 8], 2) for block in range(int(len(bin_string) / 8))]  # биты в байты 
		output = bytes(output)
		return output
 

# w = int(input("Введите размер слова в битах  (16, 32, 64): "))  # Размер слова в битах  (16, 32, 64) #256/4 or 128/4 or 64/4 default 32 
w = 32

# r = int(input("Введите кол-во раундов: "))   # Кол-во раундов
r = 20

# Key = input("Введите секретный ключ: ")  # Секретный ключ


def generateKey(Key,w,r):
	while len(Key) % w != 0:  # Дополнение ключа до кратности w
		Key =''.join([Key,"0"]) 
	c = int(len(Key) / w) # количество слов в ключе
	f = (sqrt(5) + 1) / 2 # золотое сечение      
	L = [Key[i * w : (i + 1) * w] for i in range(c)]
	L = [int('0b' + k, 2) for k in L]
	mod = 2 ** w
	def Odd(number): 
		if int(number) % 2 != 0: return int(number)          #Округление до ближайшего нечетного целого для констант 
		else:					 return int(number) + 1
	f = (sqrt(5) + 1) / 2 # золотое сечение
	Qw = Odd((f - 1) * 2 ** w)                 # magick константы
	Pw = Odd((exp(1) - 2) * 2 ** w)
	S = []
	S.append(Pw)
	for i in range(1, 2 * r + 4):
		S.append((S[i - 1] + Qw) % mod)
	A = B = i = j = 0
	v = 3 * max(c, 2*r + 4)
	for s in range(1, v):
		A = S[i] = Shift((S[i] + A + B) % mod, w, 3, 'left')
		B = L[j] = Shift((L[j] + A + B) % mod, w, (A + B)%mod, 'left')
		i = (i + 1) % (2 * r + 4)
		j = (j + 1) % c
	S = tuple(S)
	return S

@cache
def EncryptBlock(message,S, w = 32, r = 20):
		mod = 2 ** w
		A = int(''.join(['0b',message[0:w]]), 2)
		B = int(''.join(['0b',message[(w):(2 * w)]]), 2)             
		C = int(''.join(['0b',message[(2 * w):(3 * w)]]), 2)
		D = int(''.join(['0b',message[(3 * w):(4 * w)]]), 2)

		B = (B + S[0]) % mod
		D = (D + S[1]) % mod
		for i in range(1, r):
			t = Shift((B * ((2 * B) % mod + 1) % mod) % mod, w, int(log(w)), 'left')
			u = Shift((D * ((2 * D) % mod + 1) % mod) % mod, w, int(log(w)), 'left')
			A = (Shift((A^t), w, u, 'left') + S[2 * i]) % mod								
			C = (Shift((C^u), w, t, 'left') + S[2 * i + 1]) % mod
			aa, bb, cc, dd = B, C, D, A
			A, B, C, D = aa, bb, cc, dd 

		A = (A + S[2 * r + 2]) % mod
		C = (C + S[2 * r + 3]) % mod

		output = ''
		output = ''.join([output,Expand(bin(A), w)[2:]])
		output = ''.join([output,Expand(bin(B), w)[2:]])
		output = ''.join([output,Expand(bin(C), w)[2:]])
		output = ''.join([output,Expand(bin(D), w)[2:]])
		return output

@cache
def DecryptBlock(message,S, w = 32, r = 20):
		mod = 2 ** w
		
		A = int(''.join(['0b',message[0:w]]), 2)
		B = int(''.join(['0b',message[(w):(2 * w)]]), 2)                
		C = int(''.join(['0b',message[(2 * w):(3 * w)]]), 2)
		D = int(''.join(['0b',message[(3 * w):(4 * w)]]), 2)

		C = (C - S[2 * r + 3]) % mod
		A = (A - S[2 * r + 2]) % mod

		for j in range(1, r):
			i = r - j

			aa, bb, cc, dd = D, A, B, C
			A, B, C, D = aa, bb, cc, dd

			u = Shift((D * ((2 * D) % mod + 1) % mod) % mod, w, int(log(w)), 'left')
			t = Shift((B * ((2 * B) % mod + 1) % mod) % mod, w, int(log(w)), 'left')
			C = (Shift((C - S[2 * i + 1]) % mod, w, t % w, 'right')^u)
			A = (Shift((A - S[2 * i]) % mod, w, u % w, 'right')^t)

		B = (B - S[0]) % mod
		D = (D - S[1]) % mod

		output = ''
		output = ''.join([output,Expand(bin(A), w)[2:]])
		output = ''.join([output,Expand(bin(B), w)[2:]])
		output = ''.join([output,Expand(bin(C), w)[2:]])
		output = ''.join([output,Expand(bin(D), w)[2:]])
		return output

def Encription(message,S,mode,iv, w = 32, r = 20):
		
		while len(message) % (4 * w) != 0:
			message = ''.join(['0',message])	
		
		message = [message[(block * 4 * w): ((block + 1) * 4 * w)] for block in range(int(len(message) / (4 * w)))]
		output = ''
		last = iv
		last = bytes(last,'utf-8')
		last = bytesToBin(last).zfill(w*4)

		if mode == "EBC":
			for block in message :
				output = ''.join([output,EncryptBlock(block,S, w, r)])
			return output

		elif mode == "CBC":
			for block in message:
				last = XORstrings(last,block)
				last = EncryptBlock(last,S,w,r)
				output = ''.join([output,last])

		elif mode == "CFB":
			for block in message: 
				last = EncryptBlock(last,S,w,r)
				last = XORstrings(block,last)
				output = ''.join([output,last])

		elif mode == "OFB":
			for block in message:
				last = EncryptBlock(last,S,w,r)
				block = XORstrings(last,block)
				output = ''.join([output,block])
		return output


def Decription(message,S,mode,iv, w = 32, r = 20):

		message = [message[x * w * 4 : (x + 1) * w * 4] for x in range(int(len(message) / (w * 4)))]
		output = ''
		last = iv
		last = bytes(last,'utf-8')
		last = bytesToBin(last).zfill(w*4)

		if mode == "EBC":
			for block in message:
				output = ''.join([output,DecryptBlock(block,S,w,r)])

		elif mode == "CBC":
			for block in message: 
				buf = block 
				block = DecryptBlock(block,S,w,r)
				block = XORstrings(block,last) 
				output = ''.join([output,block])
				last = buf

		elif mode == "CFB":
			for block in message:
				buf = block
				last = EncryptBlock(last,S,w,r)
				last = XORstrings(last,block)
				output = ''.join([output,last])
				last = buf

		elif mode == "OFB":
			for block in message:
				last = EncryptBlock(last,S,w,r)
				block = XORstrings(last,block)
				output = ''.join([output,block])

		return output

def Encfile(filename,mode,S,iv,w=32,r=20):

	chunksize = 8192
	with open (filename,mode='rb') as file: 
		pointer = 0
		fileContent = file.read(chunksize)
		message = bytesToBin(fileContent)  
		isFirst = True 
		while fileContent:
			if isFirst:
				encription_bin_message = Encription(message, S,mode,iv,w,r)
				encription_message = binToBytes(encription_bin_message)
				isFirst = False
			else:
				file.seek(pointer)
				fileContent = file.read(chunksize)
				if len(fileContent) <= chunksize and len(fileContent)!=0:
					message = bytesToBin(fileContent)
					encription_bin_message = Encription(message, S,mode,iv,w,r)
					encription_message = binToBytes(encription_bin_message)
				elif len(fileContent) == 0:
					return

			with open(filename,mode = 'r+b') as f:
				f.seek(pointer) 
				f.write(encription_message) 
				pointer += len(encription_message)

def Decfile(filename,mode,S,iv,w=32,r=20):

	chunksize = 8192
	with open (filename,mode='r+b') as file: 
		pointer = 0
		fileContent = file.read(chunksize)
		message = bytesToBin(fileContent)
		isFirst = True
		while fileContent:
			if isFirst:
				decription_bin_message = Decription(message,S,mode,iv,w,r)
				decription_message = binToBytes(decription_bin_message)
				pointer += len(decription_message)
				decription_message = decription_message.lstrip(b'\x00')
				isFirst = False
			else: 
				file.seek(pointer)
				fileContent = file.read(chunksize)
				if len(fileContent) <= chunksize and len(fileContent)!=0:
					message = bytesToBin(fileContent)
					decription_bin_message = Decription(message, S,mode,iv,w,r)
					decription_message = binToBytes(decription_bin_message)
					pointer += len(decription_message)
					decription_message = decription_message.lstrip(b'\x00')
				elif len(fileContent) == 0:
					break
			with open("test2.txt",mode = 'a+b') as f:
				f.write(decription_message) 
				newname = os.path.realpath(f.name)

	os.remove(filename)
	os.rename(newname,filename)
	
	


def main():		
	filenameWAV = r""
	filenameTXT = r""
	filenameJPG = r""
	filenameMP4 = r""
	filenameJPGbig = r""
	mode = ""
	filename = ""
	choose = 1
	Key = "SecretKey"                                    
	Key = bytes(Key, 'utf-8') 
	Key = bytesToBin(Key)
	iv = "test" 
	S=generateKey(Key,w,r)
	if   choose == 1: filename = filenameTXT
	elif choose == 2: filename = filenameJPG
	elif choose == 3: filename = filenameWAV
	elif choose == 4: filename = filenameMP4
	elif choose == 5: filename = filenameJPGbig
	Encfile(filename,mode,S,iv,w,r)
	Decfile(filename,mode,S,iv,w,r)

if __name__== "__main__":
	main()

