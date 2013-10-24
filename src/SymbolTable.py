class Symbol:
   nxtAddress = 0
   def __init__(self,symId, symType):
      self.symId = symId
      self.symType = symType
      self.addr = Symbol.nxtAddress
      Symbol.nxtAddress+=1

class Procedure(Symbol):
   def __init__(self,name,symType,params=None,localVars=None):
      Symbol.__init__(self,name,symType)
      if params is None: params = []
      self.params=params
      if localVars is None: localVars = []
      self.localVars = localVars

   def addParam(self,sym):
      self.params.append(sym)

   def addLocalVar(self,sym):
      self.localVars.append(sym)



class SymbolTableHandler:
   def __init__(self):
      self._tables = [{}]
      self._nestLevel = 0

   def scopeEntry(self):
      self._nestLevel += 1
      self._tables.append({})

   def symbolDecl(self,s):
      currentTable = self._tables[-1]
      if(s.symId in currentTable):
         # error s is multiply declared
         return False
      else:
         currentTable[s.symId] = s
         return True

   def symbolUse(self,symId):
      tableList = list(self._tables)

      # while there are tables in the list
      while tableList:
         # remove the last table
         table = tableList.pop()
         # check if symbol is in table
         if symId in table:
            return True

      # error: s does not exist in any table
      return False

   def scopeExit(self):
      # remove the last inserted table
      self._tables.pop()
      # decrease nesting level counter
      self._nestLevel -= 1

   def getSymbol(self,symId):
      tableList = list(self._tables)

      # while there are tables in the list
      while tableList:
         # remove the last table
         table = tableList.pop()
         # check if symbol is in table
         if symId in table:
            return table[symId]

      # error: s does not exist in any table
      return None