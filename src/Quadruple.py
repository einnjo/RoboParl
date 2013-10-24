
opHierarchy = {	'*' : 0, '/' : 0, '%' : 0, 
						'+' : 1, '-' : 1,
						'<' : 2, '>' : 2, '>=' : 2, '<=' : 2,
						'==': 2, '!=': 2,
						'=' : 3 }

class Quad:
	QuadId=0
	def __init__(self, op, var1, var2, result,quadId=None):
		self.op = op;
		self.var1 = var1;
		self.var2 = var2;
		self.result = result;
		if quadId is None: quadId = Quad.QuadId
		self.quadId = quadId;
		Quad.QuadId+=1

	
	def toStr(self):
		return "#"+str(self.quadId)+" ("+str(self.op)+", "+str(self.var1)+", "+str(self.var2)+", "+str(self.result)+")"

class QuadGen:
	tmp = 0
	def __init__(self):
		self.ops = []
		self.out = []
		self.quads = []
		self.jumps = []

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
		#print op + " " + var1 + " " + var2 + " " + result 

	def assignmentQuad(self,symId):
		op = '='
		var1 = self.out.pop()
		var2 = ''
		result = symId
		self.quads.append(Quad(op,var1,var2,result))

	def falseJmp(self):
		cond = self.quads[-1].result
		quad = Quad('gotoF', cond, '', '')
		self.quads.append(quad)
		self.jumps.append(quad.quadId)
	def elseStmt(self):
		quad = Quad('goto', '', '', '')
		self.quads.append(quad)
		self.updateJmpLoc(self.jumps.pop(),Quad.QuadId)
		self.jumps.append(quad.quadId)

	def endWhile(self):
		quad = Quad('goto', '', '', '')
		self.quads.append(quad)
		self.updateJmpLoc(self.jumps.pop(), Quad.QuadId)
		self.updateJmpLoc(quad.quadId, self.jumps.pop())

	def endIf(self):
		self.updateJmpLoc(self.jumps.pop(),Quad.QuadId)

	def updateJmpLoc(self,quadId,loc):
		self.quads[quadId].result = loc

	def clearStacks(self):
		self.out = []
		self.ops = []