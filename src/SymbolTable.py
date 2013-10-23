class Symbol:
   def __init__(self,sName, sType=None):
      self.sName = sName
      self.sType = sType

class SymbolTableHandler:
   def __init__(self):
      self._tables = [{}]
      self._nestLevel = 0

   def scopeEntry(self):
      self._nestLevel += 1
      self._tables.append({})

   def symbolDecl(self,s):
      currentTable = self._tables[-1]
      if(s.sName in currentTable):
         # error s is multiply declared
         return False
      else:
         currentTable[s.sName] = s
         return True

   def symbolUse(self,s):
      tableList = list(self._tables)

      # while there are tables in the list
      while tableList:
         # remove the last table
         table = tableList.pop()
         # check if symbol is in table
         if s.sName in table:
            return True

      # error: s does not exist in any table
      return False

   def scopeExit(self):
      # remove the last inserted table
      self._tables.pop()
      # decrease nesting level counter
      self._nestLevel -= 1

   def symbolType(self,s):
      tableList = list(self._tables)

      # while there are tables in the list
      while tableList:
         # remove the last table
         table = tableList.pop()
         # check if symbol is in table
         if s.sName in table:
            return table[s.sName].sType

      # error: s does not exist in any table
      return -1