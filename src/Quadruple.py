
opHierarchy = {	'*' : 0, '/' : 0, '%' : 0, 
						'+' : 1, '-' : 1,
						'<' : 2, '>' : 2, '>=' : 2, '<=' : 2,
						'==': 3, '!=': 3,
						'=' : 4 }

class Quad:
	def __init__(self, op, var1, var2, tmp):
		self.op = op;
		self.var1 = var1;
		self.var2 = var2;
		self.tmp = tmp;
	
	def toStr(self):
		return "("+self.op+", "+self.var1+", "+self.var2+", "+self.tmp+")"

class QuadGen:
	tmp = 0
	def __init__(self):
		self.ops = []
		self.out = []
		self.quads = []

	def pushFloor(self):
		self.ops.append('(')

	def popFloor(self):
		opStack = self.ops
		outStack = self.out
		op = opStack.pop()
		while(op != '('):
			# push op to out stack
			outStack.append(op)
			self.genQuad()
			op = opStack.pop()
	
	def flushOps(self):
		opStack = self.ops
		outStack = self.out
		while(len(opStack) != 0):
			outStack.append(opStack.pop())
			self.genQuad()

	def handleOp(self, op):
		opStack = self.ops
		outStack = self.out
		# if the operator stack is empty or last op is fake floor
		if (len(opStack) == 0 or opStack[-1]=='('):
			# push op to stack
			opStack.append(op)
		# if op has less or equal hierarchy than the op on top of the stack
		elif (opHierarchy[op] >= opHierarchy[opStack[-1]]):
			# push the op on top of the stack to out stack
			outStack.append(opStack.pop())
			self.genQuad()
			self.handleOp(op)
		else:
			# push op to op stack
			opStack.append(op)

	def handleVar(self, var):
		self.out.append(var)

	def genQuad(self):
		out = self.out
		quads = self.quads
		# pop the operator and it's 2 operands from out
		op = out.pop()
		var2 = out.pop()
		var1 = out.pop()
		result = "tmp%d" %(self.tmp)
		self.tmp += 1
		quads.append(Quad(op, var1, var2, result))
		out.append(result)

	def clearStacks(self):
		self.out = []
		self.ops = []
'''
q = QuadGen()
q.handleVar('A')
q.handleOp('+')
q.handleVar('B')
q.handleOp('*')
q.handleVar('C')
q.handleOp('+')
q.handleVar('D')
q.handleOp('*')
q.pushFloor()
q.handleVar('E')
q.handleOp('*')
q.handleVar('F')
q.popFloor()
q.handleOp('<')
q.handleVar('C')
q.handleOp('+')
q.handleVar('H')
q.flushOps()
for x in q.quads:
	print(x.toStr())

q = QuadGen()
q.handleVar('1')
q.handleOp('*')
q.pushFloor()
q.handleVar('2')
q.handleOp('+')
q.handleVar('3')
q.popFloor()
q.flushOps()
for x in q.quads:
	print(x.toStr())

'''