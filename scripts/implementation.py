#-*- coding:utf-8 -*-
#
from operator import itemgetter
from phrase_table import *

class PhrasePair:

	def __init__(self,source,target):

		self.source = source
		self.target = target

	def get_source(self):

		return self.source

	def get_target(self):

		return self.target


class Hypothesis:

	def __init__(self,source='',target=''):

		self.words_covered = []
		self.phrase_pair = PhrasePair(source,target)
		self.previous_hypothesis = None
		self.score = float()
		self.output = []

	def check_overlap(self,start,end):

		if 1 in self.words_covered[start:end]:
			return True

	def update_words_covered(self,w_covered_vector,start,end):

		for i in range(len(w_covered_vector)):
			if i in range(start,end):
				self.words_covered.append(1)
			else: self.words_covered.append(w_covered_vector[i])

class Stack:

	def __init__(self):

		self.stack = []

class Decoder:

	def __init__(self,inp):

		self.inp_spl = inp.split()

		self.input_length = len(self.inp_spl)
		self.m_stacks = [Stack() for x in range(self.input_length+1)]
		self.m_phrase_pairs = [[0 for x in xrange(self.input_length)] for y in xrange(self.input_length)]
		self.pt = PhraseTable("../data/real-world-phrase-table")
		self.pt.populate_trie()

	def populate_phrase_pairs(self,order_max=4):

		for i in range(len(self.inp_spl)):
			for j in range(i+1,i+order_max):
				if i+(j-i)<=len(self.inp_spl):
					result = self.pt.retrieval(self.inp_spl[i:j])
					if result != [('Nothing found',0.0)]:
						if len(result) >= 50:
							result = sorted(result,key=itemgetter(1),reverse=True)[:50]
						phrase_pair = PhrasePair(' '.join(self.inp_spl[i:j]),result)
						self.m_phrase_pairs[i][j-1] = phrase_pair

	def test(self):

		for y in range(len(self.m_stacks)):
			print 'stack %d = %d' %(y,len(self.m_stacks[y].stack)),


	def decode(self):

		empty_hypo = Hypothesis()
		empty_hypo.words_covered = [0 for x in range(self.input_length)]
		self.m_stacks[0].stack.append(empty_hypo)

		for i in range(len(self.m_stacks)):

			current_stack = self.m_stacks[i].stack
			#sort stack
			# current_stack = sorted(current_stack,key=attrgetter('score'),reverse=True)[:self.max_stack_size]
			print 'current stack...%d::elements in it...%d' %(i,len(current_stack))

			for j in range(len(current_stack)):

				current_hypo = current_stack[j]
				self.expand(current_hypo)

	def expand(self,current_hypo):

		print 'Now expanding hypothesis..%s -> %s..%f' % (current_hypo.phrase_pair.get_source(),current_hypo.phrase_pair.get_target(),current_hypo.score)

		for start in range(self.input_length):

			for end in range(start+1,self.input_length+1):

				if not current_hypo.check_overlap(start,end):

					phrase_pairs = self.m_phrase_pairs[start][end-1]

					if phrase_pairs!=0:

						for i in range(len(phrase_pairs.target)):

							phrase_pair = phrase_pairs.target[i]

							# print phrase_pair

							new_hypo, nwc = self.extend(current_hypo,phrase_pair,start,end)

							self.m_stacks[nwc].stack.append(new_hypo)



	def extend(self,current_hypo,phrase_pair,start,end):

		new_source = current_hypo.phrase_pair.get_source() + ' ' + ' '.join(self.inp_spl[start:end])
		new_target = current_hypo.phrase_pair.get_target() + ' ' + phrase_pair[0]

		new_hypo = Hypothesis(new_source,new_target)
		new_hypo.update_words_covered(current_hypo.words_covered,start,end)
		new_hypo.previous_hypothesis = current_hypo
		new_hypo.score = current_hypo.score + phrase_pair[1]

		return new_hypo,len([x for x in new_hypo.words_covered if x==1])


if __name__=="__main__":

	deco = Decoder("das ist ein kleines haus")
	deco.populate_phrase_pairs()
	deco.decode()
	deco.test()