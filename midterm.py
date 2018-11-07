import math
import itertools
# change rows to cols
def rows(s, n):
	rows = []
	for i in range(0,len(s),n):
		rows.append(s[i:i+n])
	return rows
def row2col(s, n): 
    cols = []
    for i in range(n):
        cols.append('')
    for i in range(len(s)):
        cols[i % n] += s[i]
    return cols

## Using sbox to transposition columns
def transcols(cols, box):
    trans = []
    for sb in box:
        trans.append(cols[sb])
    return trans

# encryption
# encrypt plaintext 
def enc(p, box):
    c = ''
    trans = transcols(row2col(p, len(box)), box)
    for i in range(len(p) / len(box)):
        for t in trans:
            c += t[i]
    ci = ''
    for t in trans:
        ci += t
    return ci 

# decryption
# find reverse shift box and decrypt ciphertext
def dec(c, box):
	p = ''
	trans = transcols(rows(c, len(c) / len(box)), box)
	for i in range(len(c) / len(box)):
		for t in trans:
			p += t[i]
	return p
	
	

# Analysis ngram-frequency 
def ngram_frequency(n, s):
	elements = []
	for i in range(len(s)-n+1):
		element = s[i:i+n]
		elements.append(element)
	d = {}
	for e in sorted(set(elements)):
		d[e] = s.count(e)
	return d

def W_32(s):
	tri_dist = ngram_frequency(3, s)
	di_dist = ngram_frequency(2, s)

	magic_num = 26 
	result = '### 3_2 ###\n\n trigram     digram   W \n---------------------------------------------\n'
	l = {}
	for t,f in tri_dist.items():
		pc = (float(f) / di_dist[t[:2]]) * magic_num
		result += '  ' + t + ' ' + str(f).rjust(3) + '    ' + t[:2] + ' ' + str(di_dist[t[:2]]).rjust(3) + '   ' + str(math.log(pc,10)) + '\n'
		l[t] = math.log(pc,10)
	m = open('Dataset-3_2','w')
	m.write(result)
	m.close()
	return l

def W_21(s):
	di_dist = ngram_frequency(2, s)
	mono_dist = ngram_frequency(1, s)

	magic_num = 26 
	result = '### 2_1 ###\n\n digram     monogram   W \n---------------------------------------------\n'
	l = {}
	for d,f in di_dist.items():
		pc = (float(f) / mono_dist[d[:1]]) * magic_num
		result += '  ' + d + ' ' + str(f).rjust(3) + '    ' + d[:1] + ' ' + str(mono_dist[d[:1]]).rjust(4) + '   ' + str(math.log(pc,10)) + '\n'
		l[d] = math.log(pc,10)
	m = open('Dataset-2_1','w')
	m.write(result)
	m.close()
	return l

# vowel analysis cipher
def count_vowel(str):
	vowel = 'AEIOU'
	sum = 0
	for v in vowel:
		sum += str.count(v)
	return sum

def get_factor(no):
	factors = []
	for i in range(5,int(no ** 0.5)):
		if no % i == 0:
			factors.append(i)
			factors.append(no/i)
	return sorted(factors)

def standard_deviation(col,exp,cipher):
	result = 0
	for i in range(0,len(cipher),col):
		result += (count_vowel(cipher[i:i+col])-exp)**2 
	row = len(cipher)/col
	return result/row

def result(col,cipher):
	exp = 0.4 * col
	result = standard_deviation(col,exp,cipher)
	#cipher_matrix = ''.join(' ' + cipher[i:i+col] + ' ' + str(count_vowel(cipher[i:i+col])).rjust(5) + ' ' + str((count_vowel(cipher[i:i+col])-exp)**2).rjust(11) + '\n' for i in range(0,len(cipher),col))
	#print (str(len(cipher)/col) + ' x ' + str(col))
	#print (' cipher'.ljust(col+2) + 'vowel'.rjust(6) + '  difference(count-expective & square)')
	#print ('-' * 50)
	#print (cipher_matrix)
	print (' standard_deviation of ' + str(len(cipher)/col) + ' x ' + str(col) + ' = ' + str(result))
	return result

def vowel_analysis(s):
	factors = get_factor(len(s))
	minsd = 10 
	print ("-Executing Vowel Analysis ...\n")
	for f in factors:
		c = ''
		for j in range(len(s)/f):
			for i in range(j,len(s),len(s)/f):
				c += s[i]
		sd = result(f,c)
		if sd < minsd: # get minimun standard derivation
			minsd = sd
			ideal_col = f 
	print ('\n-By the Vowel-Analysis above,\n-I consider ' + str(len(s)/ideal_col) + ' x ' + str(ideal_col) + ' is the better way to split the ciphertext ~~\n')
	return ideal_col

# Compare original plaintext and cracked plaintext
def rate(s1, s2):
	correct = len(s1) # or len(s2)
	for x,y in zip(s1,s2):
		if x != y:
			correct -= 1
	rate = correct / float(len(s1)) * 100
	return rate


# Read plain
f = open('plain','r')
plain = f.read()
f.close()
plain = plain.replace('\n','')
plain = plain.upper()

# Read cipher
f = open('cipher','r')
cipher = f.read()
f.close()
cipher = cipher.replace(' ','')

# shift box
sbox = [0, 1, 2, 3, 18, 17, 16, 4, 5, 6, 7, 10, 9, 8, 11, 12, 13, 14, 15]

# training
model = open('model','r')
m = model.read()
for c in m:
    if (ord(c) > 122 or ord(c) < 97) and (ord(c) > 90 or ord(c) < 65):
        m = m.replace(c,'')
m = m.upper()
print ('-Training Model... \n' + m)
print ('\n Writing Dataset to files ...')
d_32 = W_32(m)
d_21 = W_21(m)
print ('\n Finish! Dataset written to files. \n')

# vowel analysis
idealcol = vowel_analysis(cipher)

# try plaintext using machine learning
columns = rows(cipher, len(cipher) / idealcol)
print ('\n-cipher rows <=> cols\n')
print (' elements in columns\n')
for s in columns:
	print (s)

# Try the first two cols (if I don't know first two cols)
pool = []
for i in range(19):
	pool.append(i)
first2 = {}
for index in itertools.permutations(pool,2):
	wsum = 0
	for a,b in zip(columns[ index[0] ], columns[ index[1] ]):
		d_gram = a + b
		if d_gram in d_21:
			wsum += d_21[d_gram]
	if wsum > 3:
		first2[index] = wsum
Wmax = 0
for k,v in first2.items():
	rsbox = [k[0], k[1]]
	notinbox = []
	for i in range(19):
		notinbox.append(i)
	for r in rsbox:
		notinbox.remove(r)

	wwsum = 0 # wsum of whole article
	while len(notinbox) != 0:
		wsum = -10
		for i in notinbox:
			sum = 0
			for a,b,c in zip(columns[rsbox[-2]], columns[rsbox[-1]], columns[i]):
				t_gram = a + b + c
				if t_gram in d_32:
					sum += d_32[t_gram]
			if sum > wsum:
				maxi = i
				wsum = sum
		rsbox.append(maxi)
		notinbox.remove(maxi)
		wwsum += wsum
	#print ('Wsum = ' + str(wwsum).rjust(14) + '  ;Rate = ' + str(rate(plain, dec(cipher,rsbox))) + '%')
	if wwsum > Wmax:
		Wmax = wwsum
		ideal_rsbox_init = rsbox
	
# If I know first two cols
#ideal_rsbox = [0,1] # reverse shift box
ideal_rsbox = ideal_rsbox_init
notinbox = []
for i in range(0,19):
	notinbox.append(i)
for r in ideal_rsbox:
	notinbox.remove(r)
while len(notinbox) != 0: 
	wsum = 0
	for i in notinbox:
		sum = 0
		for a,b,c in zip(columns[ideal_rsbox[-2]], columns[ideal_rsbox[-1]], columns[i]):
			t_gram = a + b + c
			if t_gram in d_32:
				sum += d_32[t_gram]
		if sum > wsum:
			maxi = i
			wsum = sum
	ideal_rsbox.append(maxi)
	notinbox.remove(maxi)

print ('\nreverse shift box = ' + str(ideal_rsbox))

print ('\nPlaintext = \n' + plain)
print ('\nCracked cipher (' + str(rate(plain, dec(cipher,ideal_rsbox))) + '%) = \n' + dec(cipher,ideal_rsbox))
