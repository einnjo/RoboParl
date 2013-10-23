mOp = {}
mOp['*'] = [	[
						 0,	# INT * INT = INT 				*
						 1,	# INT * DOUBLE = DOUBLE 		*
						-1,	# INT * BOOL = ERROR
						-1,	# INT * STRING = ERROR
						-1,	# INT * LIST = ERROR
						-1,	# INT * ROBOT = ERROR
					],
					[
						 1,	# DOUBLE * INT = DOUBLE 		*
						 1,	# DOUBLE * DOUBLE = DOUBLE 	*
						-1,	# DOUBLE * BOOL = ERROR
						-1,	# DOUBLE * STRING = ERROR
						-1,	# DOUBLE * LIST = ERROR
						-1,	# DOUBLE * ROBOT = ERROR
					],
					[
						-1,	# BOOL * INT = ERROR
						-1,	# BOOL * DOUBLE = ERROR
						-1,	# BOOL * BOOL = ERROR
						-1,	# BOOL * STRING = ERROR
						-1,	# BOOL * LIST = ERROR
						-1,	# BOOL * ROBOT = ERROR
					],
					[
						-1,	# STRING * INT = ERROR
						-1,	# STRING * DOUBLE = ERROR
						-1,	# STRING * BOOL = ERROR
						-1,	# STRING * STRING = ERROR
						-1,	# STRING * LIST = ERROR
						-1,	# STRING * ROBOT = ERROR
					],
					[
						-1,	# LIST * INT = ERROR
						-1,	# LIST * DOUBLE = ERROR
						-1,	# LIST * BOOL = ERROR
						-1,	# LIST * STRING = ERROR
						-1,	# LIST * LIST = ERROR
						-1,	# LIST * ROBOT = ERROR
					],
				
				]
mOp['/'] = [	[
						 0,	# INT / INT = INT 				*
						 1,	# INT / DOUBLE = DOUBLE 		*
						-1,	# INT / BOOL = ERROR
						-1,	# INT / STRING = ERROR
						-1,	# INT / LIST = ERROR
						-1,	# INT / ROBOT = ERROR
					],
					[
						 0,	# DOUBLE / INT = DOUBLE 		*
						 1,	# DOUBLE / DOUBLE = DOUBLE 	*
						-1,	# DOUBLE / BOOL = ERROR
						-1,	# DOUBLE / STRING = ERROR
						-1,	# DOUBLE / LIST = ERROR
						-1,	# DOUBLE / ROBOT = ERROR
					],
					[
						-1,	# BOOL / INT = ERROR
						-1,	# BOOL / DOUBLE = ERROR
						-1,	# BOOL / BOOL = ERROR
						-1,	# BOOL / STRING = ERROR
						-1,	# BOOL / LIST = ERROR
						-1,	# BOOL / ROBOT = ERROR
					],
					[
						-1,	# STRING / INT = ERROR
						-1,	# STRING / DOUBLE = ERROR
						-1,	# STRING / BOOL = ERROR
						-1,	# STRING / STRING = ERROR
						-1,	# STRING / LIST = ERROR
						-1,	# STRING / ROBOT = ERROR
					],
					[
						-1,	# LIST / INT = ERROR
						-1,	# LIST / DOUBLE = ERROR
						-1,	# LIST / BOOL = ERROR
						-1,	# LIST / STRING = ERROR
						-1,	# LIST / LIST = ERROR
						-1,	# LIST / ROBOT = ERROR
					],
				
				]
mOp['%'] = [	[
						 0,	# INT % INT = INT
						 1,	# INT % DOUBLE = DOUBLE
						-1,	# INT % BOOL = ERROR
						-1,	# INT % STRING = ERROR
						-1,	# INT % LIST = ERROR
						-1,	# INT % ROBOT = ERROR
					],
					[
						 1,	# DOUBLE % INT = DOUBLE
						 1,	# DOUBLE % DOUBLE = DOUBLE
						-1,	# DOUBLE % BOOL = ERROR
						-1,	# DOUBLE % STRING = ERROR
						-1,	# DOUBLE % LIST = ERROR
						-1,	# DOUBLE % ROBOT = ERROR
					],
					[
						-1,	# BOOL % INT = ERROR
						-1,	# BOOL % DOUBLE = ERROR
						-1,	# BOOL % BOOL = ERROR
						-1,	# BOOL % STRING = ERROR
						-1,	# BOOL % LIST = ERROR
						-1,	# BOOL % ROBOT = ERROR
					],
					[
						-1,	# STRING % INT = ERROR
						-1,	# STRING % DOUBLE = ERROR
						-1,	# STRING % BOOL = ERROR
						-1,	# STRING % STRING = ERROR
						-1,	# STRING % LIST = ERROR
						-1,	# STRING % ROBOT = ERROR
					],
					[
						-1,	# LIST % INT = ERROR
						-1,	# LIST % DOUBLE = ERROR
						-1,	# LIST % BOOL = ERROR
						-1,	# LIST % STRING = ERROR
						-1,	# LIST % LIST = ERROR
						-1,	# LIST % ROBOT = ERROR
					],
				
				]
mOp['+'] = [	[
						 0,	# INT + INT = INT
						 1,	# INT + DOUBLE = DOUBLE
						-1,	# INT + BOOL = ERROR
						-1,	# INT + STRING = ERROR
						-1,	# INT + LIST = ERROR
						-1,	# INT + ROBOT = ERROR
					],
					[
						 1,	# DOUBLE + INT = DOUBLE 		*
						 1,	# DOUBLE + DOUBLE = DOUBLE 	*
						-1,	# DOUBLE + BOOL = ERROR
						-1,	# DOUBLE + STRING = ERROR
						-1,	# DOUBLE + LIST = ERROR
						-1,	# DOUBLE + ROBOT = ERROR
					],
					[
						-1,	# BOOL + INT = ERROR
						-1,	# BOOL + DOUBLE = ERROR
						-1,	# BOOL + BOOL = ERROR
						-1,	# BOOL + STRING = ERROR
						-1,	# BOOL + LIST = ERROR
						-1,	# BOOL + ROBOT = ERROR
					],
					[
						-1,	# STRING + INT = ERROR
						-1,	# STRING + DOUBLE = ERROR
						-1,	# STRING + BOOL = ERROR
						 3,	# STRING + STRING = STRING 	*
						-1,	# STRING + LIST = ERROR
						-1,	# STRING + ROBOT = ERROR
					],
					[
						-1,	# LIST + INT = ERROR
						-1,	# LIST + DOUBLE = ERROR
						-1,	# LIST + BOOL = ERROR
						-1,	# LIST + STRING = ERROR
						-1,	# LIST + LIST = ERROR
						-1,	# LIST + ROBOT = ERROR
					],
				
				]
mOp['-'] = [	[
						 0,	# INT - INT = INT 				*
						 1,	# INT - DOUBLE = DOUBLE 		*
						-1,	# INT - BOOL = ERROR
						-1,	# INT - STRING = ERROR
						-1,	# INT - LIST = ERROR
						-1,	# INT - ROBOT = ERROR
					],
					[
						 1,	# DOUBLE - INT = DOUBLE 		*
						 1,	# DOUBLE - DOUBLE = DOUBLE 	*
						-1,	# DOUBLE - BOOL = ERROR
						-1,	# DOUBLE - STRING = ERROR
						-1,	# DOUBLE - LIST = ERROR
						-1,	# DOUBLE - ROBOT = ERROR
					],
					[
						-1,	# BOOL - INT = ERROR
						-1,	# BOOL - DOUBLE = ERROR
						-1,	# BOOL - BOOL = ERROR
						-1,	# BOOL - STRING = ERROR
						-1,	# BOOL - LIST = ERROR
						-1,	# BOOL - ROBOT = ERROR
					],
					[
						-1,	# STRING - INT = ERROR
						-1,	# STRING - DOUBLE = ERROR
						-1,	# STRING - BOOL = ERROR
						-1,	# STRING - STRING = ERROR
						-1,	# STRING - LIST = ERROR
						-1,	# STRING - ROBOT = ERROR
					],
					[
						-1,	# LIST - INT = ERROR
						-1,	# LIST - DOUBLE = ERROR
						-1,	# LIST - BOOL = ERROR
						-1,	# LIST - STRING = ERROR
						-1,	# LIST - LIST = ERROR
						-1,	# LIST - ROBOT = ERROR
					],
				
				]
mOp['='] = [	[
						 0,	# INT = INT = INT 				*
						-1,	# INT = DOUBLE = ERROR 		
						-1,	# INT = BOOL = ERROR
						-1,	# INT = STRING = ERROR
						-1,	# INT = LIST = ERROR
						-1,	# INT = ROBOT = ERROR
					],
					[
						-1,	# DOUBLE = INT = ERROR 		
						 1,	# DOUBLE = DOUBLE = DOUBLE 	*
						-1,	# DOUBLE = BOOL = ERROR
						-1,	# DOUBLE = STRING = ERROR
						-1,	# DOUBLE = LIST = ERROR
						-1,	# DOUBLE = ROBOT = ERROR
					],
					[
						-1,	# BOOL = INT = ERROR
						-1,	# BOOL = DOUBLE = ERROR
						 2,	# BOOL = BOOL = BOOL				*
						-1,	# BOOL = STRING = ERROR
						-1,	# BOOL = LIST = ERROR
						-1,	# BOOL = ROBOT = ERROR
					],
					[
						-1,	# STRING = INT = ERROR
						-1,	# STRING = DOUBLE = ERROR
						-1,	# STRING = BOOL = ERROR
						 3,	# STRING = STRING = STRING		*
						-1,	# STRING = LIST = ERROR
						-1,	# STRING = ROBOT = ERROR
					],
					[
						-1,	# LIST = INT = ERROR
						-1,	# LIST = DOUBLE = ERROR
						-1,	# LIST = BOOL = ERROR
						-1,	# LIST = STRING = ERROR
						 4,	# LIST = LIST = LIST				*
						-1,	# LIST = ROBOT = ERROR
					],
				
				]
mOp['=='] = [	[
						2,	# INT == INT = INT 				*
						2,	# INT == DOUBLE = BOOL 		
						2,	# INT == BOOL = BOOL
						2,	# INT == STRING = BOOL
						2,	# INT == LIST = BOOL
						2,	# INT == ROBOT = BOOL
					],
					[
						2,	# DOUBLE == INT = BOOL 		
						 1,	# DOUBLE == DOUBLE = DOUBLE 	*
						2,	# DOUBLE == BOOL = BOOL
						2,	# DOUBLE == STRING = BOOL
						2,	# DOUBLE == LIST = BOOL
						2,	# DOUBLE == ROBOT = BOOL
					],
					[
						2,	# BOOL == INT = BOOL
						2,	# BOOL == DOUBLE = BOOL
						 2,	# BOOL == BOOL = BOOL				*
						2,	# BOOL == STRING = BOOL
						2,	# BOOL == LIST = BOOL
						2,	# BOOL == ROBOT = BOOL
					],
					[
						2,	# STRING == INT = BOOL
						2,	# STRING == DOUBLE = BOOL
						2,	# STRING == BOOL = BOOL
						 3,	# STRING == STRING = STRING		*
						2,	# STRING == LIST = BOOL
						2,	# STRING == ROBOT = BOOL
					],
					[
						2,	# LIST == INT = BOOL
						2,	# LIST == DOUBLE = BOOL
						2,	# LIST == BOOL = BOOL
						2,	# LIST == STRING = BOOL
						2,	# LIST == LIST = LIST				*
						2,	# LIST == ROBOT = BOOL
					],
				
				]


class SemAnalysis:
	def __init__(self):
		self.typeStack = []
		self.opStack = []

	def pushType(self, t):
		self.typeStack.append(t)

	def pushOp(self, op):
		self.opStack.append(op)

	def checkOp(self):
		op = self.opStack.pop()
		t2 = self.typeStack.pop()
		t1 = self.typeStack.pop()
		result = mOp[op][t1][t2]
		if(result == -1):
			self.typeStack.append(t1)
			return False
		else:
			self.typeStack.append(result)
			return True
			