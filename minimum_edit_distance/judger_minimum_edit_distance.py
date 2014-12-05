import sys
import time


dis = [[ sys.maxint  for x in range(2048)] for x in range(2048)]
ops = [[ '' for x in range(2048)] for x in range(2048)]

matches = []
i_words_a = []
i_words_b = []

def print_matrix(matrix,l,r):
	for i in range(l):
		for j in range(r):
			sys.stdout.write( str(matrix[i][j])+" ")
		sys.stdout.write("\n")

def back_trace(i,j):
	print i,j,ops[i][j]
	if i == 0 and j == 0: return
	else:
		if ops[i][j] == 'd':
			back_trace(i-1,j)
		elif ops[i][j] == 'i':
			back_trace(i,j-1)
		elif ops[i][j] == 'm':
			matches.append(i_words_a[i-1])
			back_trace(i-1,j-1)
		else: back_trace(i-1,j-1)

def back_trace_no_recursion(i,j):
	while(i > 0 and j > 0):
		if ops[i][j] == 'd':
			i = i - 1
		elif ops[i][j] == 'i':
			j = j -1
		elif ops[i][j] == 'm':
			matches.append(i_words_a[i-1])
			i = i -1
			j = j -1
		else: 
			i = i - 1
			j = j - 1

def main():


        file_a = open("a5.txt","r")
        file_b = open("b5.txt","r")

	begin_time = time.time()

        words_a =[x for x in(file_a.read().replace("\n"," ").replace("."," ").replace(","," ").replace("\""," ").replace("\'"," ").lower().split(" ")) if x is not '']
        words_b =[x for x in(file_b.read().replace("\n"," ").replace("."," ").replace(","," ").replace("\""," ").replace("\'"," ").lower().split(" ")) if x is not '']
        set_a = set(words_a)
        set_b = set(words_b)
        intersection  = set_a & set_b
#       print words_a
#       print words_b
	global i_words_a
	global i_words_b

        for w in words_a:
                if (w in intersection):
                        i_words_a.append(w)

        for w in words_b:
                if (w in intersection):
                        i_words_b.append(w)

	i_words_a = words_a
	i_words_b = words_b
#	for i in range(len(i_words_a)):
#		print i,i_words_a[i]
#	for j in range(len(i_words_b)):
#		print j,i_words_b[j]	

	dis[0][0] = 0;
#	print i_words_a
#	print i_words_b

	for i in  range(len(i_words_a)+1):
		for j in  range(len(i_words_b)+1):
			if i > 0 :
				dis[i][j] = min(dis[i][j],dis[i-1][j]+1) # delete
				ops[i][j] = ops[i][j] if dis[i][j] < dis[i-1][j] +1  else 'd'
			if j > 0 :
				dis[i][j] = min(dis[i][j],dis[i][j-1]+1) # insert
				ops[i][j] = ops[i][j] if dis[i][j] < dis[i][j-1] +1  else 'i'
			#substitue
			if i> 0 and j > 0:
				if i_words_a[i-1] != i_words_b[j-1]:
					dis[i][j] = min(dis[i][j],dis[i-1][j-1] + 2)
					ops[i][j] = ops[i][j] if dis[i][j] < dis[i-1][j-1] +2  else 's'
				else:
					dis[i][j] = min(dis[i][j],dis[i-1][j-1])
					ops[i][j] = ops[i][j] if dis[i][j] < dis[i-1][j-1]  else 'm'

	back_trace_no_recursion(len(i_words_a),len(i_words_b))
	matches_n = [ i for i in reversed(matches)]
	print "Matches:",matches_n

#	print "min edit distance is %d, total of B: %d, ratio: %.2f " % (dis[len(i_words_a)][len(i_words_b)],len(i_words_b), 1.0*(len(i_words_b) - dis[len(i_words_a)][len(i_words_b)])/len(i_words_b))
	print "Match Items is %d, tokens of voice recognition text : %d, recognition ratio: %.2f " % (len(matches),len(i_words_b), 1.0*len(matches)/len(i_words_b))
	end_time = time.time()

	print "Time cost: %d ms" % ((end_time - begin_time)*1000)

if __name__ == '__main__':
	main()
