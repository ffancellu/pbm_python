#-*- coding:utf-8 -*-
#

import json
import uuid

from client import client
from operator import itemgetter, attrgetter
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
		self.uuid = str(uuid.uuid4())
		self.dep_info = []

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
		self.pt = PhraseTable("../data/small-phrase-table")
		self.pt.populate_trie()

		self.best_score = [-1000.00 for x in range(self.input_length+1)]

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

		self.best_score[0] = empty_hypo.score

		for i in range(len(self.m_stacks)):

			current_stack = self.m_stacks[i].stack
			
			if i!=0:
				#sending batch of sentences to the server for dep parsing
				to_send = json.dumps(map(lambda x: {'uuid':x.uuid,'sentence':x.phrase_pair.get_target()},current_stack))
				responset = json.loads(json.loads(client(to_send))["result"])

				for hyp in current_stack:
					hyp.def_info = responset['response'][hyp.uuid]

					print hyp.def_info

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

							if new_hypo.score > self.best_score[nwc]:
								self.best_score[nwc] = new_hypo.score

							# print self.best_score
							# self.prune(nwc)


	def prune(self,nwc):

		self.m_stacks[nwc].stack = sorted(self.m_stacks[nwc].stack,key=attrgetter('score'),reverse=True)
		for i in range(len(self.m_stacks[nwc].stack)):
			if self.m_stacks[nwc].stack[i].score < (self.best_score[nwc] - 0.5):
				self.m_stacks[nwc].stack = self.m_stacks[nwc].stack[:i]
				break



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