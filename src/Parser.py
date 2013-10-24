#-------------------------------------------------------------------------
#Parser.py -- ATG file parser
#Compiler Generator Coco/R,
#Copyright (c) 1990, 2004 Hanspeter Moessenboeck, University of Linz
#extended by M. Loeberbauer & A. Woess, Univ. of Linz
#ported from Java to Python by Ronald Longo
#
#This program is free software; you can redistribute it and/or modify it
#under the terms of the GNU General Public License as published by the
#Free Software Foundation; either version 2, or (at your option) any
#later version.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#As an exception, it is allowed to write an extension of Coco/R that is
#used as a plugin in non-free software.
#
#If not otherwise stated, any source code generated by Coco/R (other than
#Coco/R itself) does not fall under the GNU General Public License.
#-------------------------------------------------------------------------*/

from SymbolTable import *
from Quadruple import Quad
from Quadruple import QuadGen
from Quadruple import opHierarchy
from Semantics import mOp
from Semantics import SemAnalysis


import sys

from Scanner import Token
from Scanner import Scanner
from Scanner import Position

class ErrorRec( object ):
   def __init__( self, l, c, s ):
      self.line   = l
      self.col    = c
      self.num    = 0
      self.str    = s


class Errors( object ):
   errMsgFormat = "file %(file)s : (%(line)d, %(col)d) %(text)s\n"
   eof          = False
   count        = 0         # number of errors detected
   fileName     = ''
   listName     = ''
   mergeErrors  = False
   mergedList   = None      # PrintWriter
   errors       = [ ]
   minErrDist   = 2
   errDist      = minErrDist
      # A function with prototype: f( errorNum=None ) where errorNum is a
      # predefined error number.  f returns a tuple, ( line, column, message )
      # such that line and column refer to the location in the
      # source file most recently parsed.  message is the error
      # message corresponging to errorNum.

   @staticmethod
   def Init( fn, dir, merge, getParsingPos, errorMessages ):
      Errors.theErrors = [ ]
      Errors.getParsingPos = getParsingPos
      Errors.errorMessages = errorMessages
      Errors.fileName = fn
      listName = dir + 'listing.txt'
      Errors.mergeErrors = merge
      if Errors.mergeErrors:
         try:
            Errors.mergedList = open( listName, 'w' )
         except IOError:
            raise RuntimeError( '-- Compiler Error: could not open ' + listName )

   @staticmethod
   def storeError( line, col, s ):
      if Errors.mergeErrors:
         Errors.errors.append( ErrorRec( line, col, s ) )
      else:
         Errors.printMsg( Errors.fileName, line, col, s )

   @staticmethod
   def SynErr( errNum, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      msg = Errors.errorMessages[ errNum ]
      Errors.storeError( line, col, msg )
      Errors.count += 1

   @staticmethod
   def SemErr( errMsg, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      Errors.storeError( line, col, errMsg )
      Errors.count += 1

   @staticmethod
   def Warn( errMsg, errPos=None ):
      line,col = errPos if errPos else Errors.getParsingPos( )
      Errors.storeError( line, col, errMsg )

   @staticmethod
   def Exception( errMsg ):
      print errMsg
      sys.exit( 1 )

   @staticmethod
   def printMsg( fileName, line, column, msg ):
      vals = { 'file':fileName, 'line':line, 'col':column, 'text':msg }
      sys.stdout.write( Errors.errMsgFormat % vals )

   @staticmethod
   def display( s, e ):
      Errors.mergedList.write('**** ')
      for c in xrange( 1, e.col ):
         if s[c-1] == '\t':
            Errors.mergedList.write( '\t' )
         else:
            Errors.mergedList.write( ' ' )
      Errors.mergedList.write( '^ ' + e.str + '\n')

   @staticmethod
   def Summarize( sourceBuffer ):
      if Errors.mergeErrors:
         # Initialize the line iterator
         srcLineIter = iter(sourceBuffer)
         srcLineStr  = srcLineIter.next( )
         srcLineNum  = 1

         try:
            # Initialize the error iterator
            errIter = iter(Errors.errors)
            errRec  = errIter.next( )

            # Advance to the source line of the next error
            while srcLineNum < errRec.line:
               Errors.mergedList.write( '%4d %s\n' % (srcLineNum, srcLineStr) )

               srcLineStr = srcLineIter.next( )
               srcLineNum += 1

            # Write out all errors for the current source line
            while errRec.line == srcLineNum:
               Errors.display( srcLineStr, errRec )

               errRec = errIter.next( )
         except:
            pass

         # No more errors to report
         try:
            # Advance to end of source file
            while True:
               Errors.mergedList.write( '%4d %s\n' % (srcLineNum, srcLineStr) )

               srcLineStr = srcLineIter.next( )
               srcLineNum += 1
         except:
            pass

         Errors.mergedList.write( '\n' )
         Errors.mergedList.write( '%d errors detected\n' % Errors.count )
         Errors.mergedList.close( )

      sys.stdout.write( '%d errors detected\n' % Errors.count )
      if (Errors.count > 0) and Errors.mergeErrors:
         sys.stdout.write( 'see ' + Errors.listName + '\n' )


class Parser( object ):
   _EOF = 0
   _idConst = 1
   _intConst = 2
   _doubleConst = 3
   _stringConst = 4
   maxT = 71

   T          = True
   x          = False
   minErrDist = 2

   TYPES = {'Int': 0, 'Double' : 1, 'Bool' : 2, 'String' : 3, 'List' : 4, 'Robot' : 5, 'Void' : 6}
   TYPE_LIST = ['Int', 'Double', 'Bool', 'String', 'List', 'Robot', 'Void']
   symTable = SymbolTableHandler()
   semA = SemAnalysis()
   quads = QuadGen()
   typeStack = []
   currentProc = None

   def declareVar(self, sym):
      if not self.symTable.symbolDecl(sym):
         self.SemErr("Symbol %s is already defined." %sym.symId)

   def useVar(self, symId):
      if not self.symTable.symbolUse(symId):
         self.SemErr("Symbol %s is undefined." %symId)

   def getType(self, t):
      return self.TYPES[t]

   def typeVar(self,symId):
      if self.symTable.getSymbol(symId) is not None:
         return self.symTable.getSymbol(symId).symType
      else:
         return -1


   def __init__( self ):
      self.scanner     = None
      self.token       = None           # last recognized token
      self.la          = None           # lookahead token
      self.genScanner  = False
      self.tokenString = ''             # used in declarations of literal tokens
      self.noString    = '-none-'       # used in declarations of literal tokens
      self.errDist     = Parser.minErrDist

   def getParsingPos( self ):
      return self.la.line, self.la.col

   def SynErr( self, errNum ):
      if self.errDist >= Parser.minErrDist:
         Errors.SynErr( errNum )

      self.errDist = 0

   def SemErr( self, msg ):
      if self.errDist >= Parser.minErrDist:
         Errors.SemErr( msg )

      self.errDist = 0

   def Warning( self, msg ):
      if self.errDist >= Parser.minErrDist:
         Errors.Warn( msg )

      self.errDist = 0

   def Successful( self ):
      return Errors.count == 0;

   def LexString( self ):
      return self.token.val

   def LookAheadString( self ):
      return self.la.val

   def Get( self ):
      while True:
         self.token = self.la
         self.la = self.scanner.Scan( )
         if self.la.kind <= Parser.maxT:
            self.errDist += 1
            break
         
         self.la = self.token

   def Expect( self, n ):
      if self.la.kind == n:
         self.Get( )
      else:
         self.SynErr( n )

   def StartOf( self, s ):
      return self.set[s][self.la.kind]

   def ExpectWeak( self, n, follow ):
      if self.la.kind == n:
         self.Get( )
      else:
         self.SynErr( n )
         while not self.StartOf(follow):
            self.Get( )

   def WeakSeparator( self, n, syFol, repFol ):
      s = [ False for i in xrange( Parser.maxT+1 ) ]
      if self.la.kind == n:
         self.Get( )
         return True
      elif self.StartOf(repFol):
         return False
      else:
         for i in xrange( Parser.maxT ):
            s[i] = self.set[syFol][i] or self.set[repFol][i] or self.set[0][i]
         self.SynErr( n )
         while not s[self.la.kind]:
            self.Get( )
         return self.StartOf( syFol )

   def RoboParl( self ):
      self.Expect(5)
      # declare global procedure
      proc = Procedure("__Global__",-1)
      self.declareVar(proc)
      self.currentProc = proc 
      
      if (self.la.kind == 1 or self.la.kind == 7):
         self.GlobalVars()
      self.Tasks()
      self.Expect(6)
      for x in self.quads.quads:
         print(x.toStr())
      

   def GlobalVars( self ):
      if self.la.kind == 7:
         self.VarDec()
      elif self.la.kind == 1:
         self.VarOp()
      else:
         self.SynErr(72)
      if (self.la.kind == 1 or self.la.kind == 7):
         self.NxtGlobalVar()

   def Tasks( self ):
      while not (self.StartOf(1)):
         self.SynErr(73)
         self.Get()
      type = self.Type()
      self.Expect(35)
      self.Expect(1)
      # declare a new procedure in the table
      procId = self.LexString()
      proc = Procedure(procId,type) 
      self.declareVar(proc)
            # enter a new scope
      self.symTable.scopeEntry()
            # set current procedure
      self.currentProc = proc
      
      self.Expect(28)
      if (self.StartOf(2)):
         self.Params()
      self.Expect(29)
      # set procedures starting point
      proc.addr = Quad.QuadId+1
      
      self.Block()
      self.Expect(6)
      # exit scope
      self.symTable.scopeExit()
      
      if (self.StartOf(2)):
         self.NxtTask()

   def VarDec( self ):
      while not (self.la.kind == 0 or self.la.kind == 7):
         self.SynErr(74)
         self.Get()
      self.Expect(7)
      type = self.Type()
      self.Expect(1)
      # declare a new symbol in the table
      symId = self.LexString() 
      sym = Symbol(symId,type)
      self.declareVar(sym)
            # add symbol to procedures local variables
      self.currentProc.addLocalVar(sym)
      print ("Se agrego a proc %s la var %s" % (self.currentProc.symId, symId))
            
      if (self.la.kind == 8):
         self.Get( )
         self.semA.pushType(type)
         self.semA.pushOp(self.LexString())
         
         
         self.Expression()
         self.quads.assignmentQuad(symId)
         if not self.semA.checkOp():
            self.SemErr("Invalid assginment")
         
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(75)
         self.Get()
      self.Expect(9)

   def VarOp( self ):
      self.Expect(1)
      # check if id is declared
      sym = self.symTable.getSymbol(self.LexString())
      if sym is None:
         self.SemErr("Symbol %s is undefined." %self.LexString())
            
      if self.la.kind == 45:
         self.RobotFunc()
      elif self.la.kind == 8:
         self.Get( )
         self.semA.pushType(sym.symType)
         self.semA.pushOp(self.LexString())
                  
         self.Expression()
         self.quads.assignmentQuad(sym.symId)
         if not self.semA.checkOp():
            self.SemErr("Invalid assginment")
         
      elif self.la.kind == 28:
         self.TaskCall()
      else:
         self.SynErr(76)
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(77)
         self.Get()
      self.Expect(9)

   def NxtGlobalVar( self ):
      self.GlobalVars()

   def Type( self ):
      while not (self.StartOf(1)):
         self.SynErr(78)
         self.Get()
      if self.la.kind == 10:
         self.Get( )
      elif self.la.kind == 11:
         self.Get( )
      elif self.la.kind == 12:
         self.Get( )
      elif self.la.kind == 13:
         self.Get( )
      elif self.la.kind == 14:
         self.Get( )
      elif self.la.kind == 15:
         self.Get( )
      elif self.la.kind == 16:
         self.Get( )
      else:
         self.SynErr(79)
      if(self.LexString() not in self.TYPE_LIST):
         self.SemErr("Invalid Type %s" %(self.LexString()))
         type = 0
      else:
         type = self.TYPES[self.LexString()]
      
      
      return type

   def Expression( self ):
      self.Exp()
      if (self.StartOf(3)):
         if self.la.kind == 17:
            self.Get( )
         elif self.la.kind == 18:
            self.Get( )
         elif self.la.kind == 19:
            self.Get( )
         elif self.la.kind == 20:
            self.Get( )
         elif self.la.kind == 21:
            self.Get( )
         else:
            self.Get( )
         self.quads.handleOp(self.LexString())
         self.semA.pushOp(self.LexString())              
         
         self.Exp()
         if not self.semA.checkOp():
            self.SemErr("Invalid operation")
                  
      self.quads.flushOps()
            

   def RobotFunc( self ):
      self.Expect(45)
      if self.StartOf(4):
         self.RobotLook()
      elif self.StartOf(5):
         self.RobotPaint()
      elif self.StartOf(6):
         self.RobotWall()
      elif self.la.kind == 68 or self.la.kind == 69 or self.la.kind == 70:
         self.RobotMove()
      else:
         self.SynErr(80)

   def TaskCall( self ):
      self.Expect(28)
      self.Arguments()
      self.Expect(29)

   def Exp( self ):
      self.Term()
      if (self.la.kind == 23 or self.la.kind == 24):
         if self.la.kind == 23:
            self.Get( )
         else:
            self.Get( )
         self.quads.handleOp(self.LexString())
         self.semA.pushOp(self.LexString())
         
         
         self.Exp()
         if not self.semA.checkOp():
            self.SemErr("Invalid operation")
         

   def Term( self ):
      self.Factor()
      if (self.la.kind == 25 or self.la.kind == 26 or self.la.kind == 27):
         if self.la.kind == 25:
            self.Get( )
         elif self.la.kind == 26:
            self.Get( )
         else:
            self.Get( )
         self.semA.pushOp(self.LexString())
         self.quads.handleOp(self.LexString())
         
         
         self.Term()
         if not self.semA.checkOp():
            self.SemErr("Invalid operation")
         

   def Factor( self ):
      if self.la.kind == 28:
         self.Get( )
         self.quads.pushFloor()
         
         
         self.Expression()
         self.Expect(29)
         self.quads.popFloor()
         
         
      elif self.la.kind == 24:
         self.Get( )
         self.Constant()
      elif self.StartOf(7):
         self.Constant()
      else:
         self.SynErr(81)

   def Constant( self ):
      if self.la.kind == 1:
         self.Get( )
         symId = self.LexString()
         self.useVar(symId)
         symType = self.typeVar(symId)
         self.semA.pushType(symType)
         self.quads.handleVar(symId)
         
         
      elif self.la.kind == 2:
         self.Get( )
         self.quads.handleVar(self.LexString())
         self.semA.pushType(0)
         
      elif self.la.kind == 3:
         self.Get( )
         self.quads.handleVar(self.LexString()) 
         self.semA.pushType(1)
         
      elif self.la.kind == 30:
         self.Get( )
         self.quads.handleVar(self.LexString())
         self.semA.pushType(2)
                  
      elif self.la.kind == 31:
         self.Get( )
         self.quads.handleVar(self.LexString())
         self.semA.pushType(2)
                  
      elif self.la.kind == 4:
         self.Get( )
         self.quads.handleVar(self.LexString()) 
         self.semA.pushType(3)
         
      elif self.la.kind == 32:
         self.List()
         self.semA.pushType(4)
         
      else:
         self.SynErr(82)

   def List( self ):
      self.Expect(32)
      self.ListItems()
      self.Expect(33)

   def ListItems( self ):
      self.Expression()
      if (self.la.kind == 34):
         self.NxtListItem()

   def NxtListItem( self ):
      self.Expect(34)
      self.ListItems()

   def Arguments( self ):
      self.Expression()
      if (self.la.kind == 34):
         self.NxtArgument()

   def NxtArgument( self ):
      self.Expect(34)
      self.Arguments()

   def Params( self ):
      while not (self.StartOf(1)):
         self.SynErr(83)
         self.Get()
      type = self.Type()
      self.Expect(1)
      # parameter declaration
      symId = self.LexString()
      sym = Symbol(symId,type)
      self.declareVar(sym)
            # add parameter to procedure
      self.currentProc.addParam(sym)
      print ("Se agrego a proc %s el parametro %s" % (self.currentProc.symId, symId))
                        
      if (self.la.kind == 34):
         self.NxtParam()

   def Block( self ):
      if self.la.kind == 7:
         self.VarDec()
      elif self.la.kind == 1:
         self.VarOp()
      elif self.la.kind == 36:
         self.IfStmt()
      elif self.la.kind == 38:
         self.WhileStmt()
      elif self.la.kind == 39:
         self.ForStmt()
      elif self.la.kind == 41:
         self.WriteStmt()
      elif self.la.kind == 42:
         self.ReadStmt()
      elif self.la.kind == 43:
         self.ResturnStmt()
      elif self.la.kind == 28:
         self.TaskCall()
      elif self.la.kind == 44:
         self.BreakStmt()
      else:
         self.SynErr(84)
      if (self.StartOf(8)):
         self.NxtBlock()

   def NxtTask( self ):
      self.Tasks()

   def NxtParam( self ):
      self.Expect(34)
      self.Params()

   def IfStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 36):
         self.SynErr(85)
         self.Get()
      self.Expect(36)
      self.Expect(28)
      self.Expression()
      self.Expect(29)
      self.quads.falseJmp()
      
      self.Block()
      if (self.la.kind == 37):
         while not (self.la.kind == 0 or self.la.kind == 37):
            self.SynErr(86)
            self.Get()
         self.quads.elseStmt()
         
         self.Get( )
         self.Block()
      self.quads.endIf()
      
      while not (self.la.kind == 0 or self.la.kind == 6):
         self.SynErr(87)
         self.Get()
      self.Expect(6)

   def WhileStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 38):
         self.SynErr(88)
         self.Get()
      self.Expect(38)
      self.Expect(28)
      self.quads.jumps.append(Quad.QuadId)
      
      self.Expression()
      self.quads.falseJmp()
            
      self.Expect(29)
      self.Block()
      self.quads.endWhile()
      
      while not (self.la.kind == 0 or self.la.kind == 6):
         self.SynErr(89)
         self.Get()
      self.Expect(6)

   def ForStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 39):
         self.SynErr(90)
         self.Get()
      self.Expect(39)
      self.Expect(1)
      self.Expect(40)
      self.Range()
      self.Block()
      while not (self.la.kind == 0 or self.la.kind == 6):
         self.SynErr(91)
         self.Get()
      self.Expect(6)

   def WriteStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 41):
         self.SynErr(92)
         self.Get()
      self.Expect(41)
      self.Expect(28)
      self.Expression()
      self.Expect(29)
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(93)
         self.Get()
      self.Expect(9)

   def ReadStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 42):
         self.SynErr(94)
         self.Get()
      self.Expect(42)
      self.Expect(28)
      self.Expect(1)
      self.Expect(29)
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(95)
         self.Get()
      self.Expect(9)

   def ResturnStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 43):
         self.SynErr(96)
         self.Get()
      self.Expect(43)
      self.Expression()
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(97)
         self.Get()
      self.Expect(9)

   def BreakStmt( self ):
      while not (self.la.kind == 0 or self.la.kind == 44):
         self.SynErr(98)
         self.Get()
      self.Expect(44)
      while not (self.la.kind == 0 or self.la.kind == 9):
         self.SynErr(99)
         self.Get()
      self.Expect(9)

   def NxtBlock( self ):
      self.Block()

   def Range( self ):
      self.Expect(28)
      self.Expression()
      self.Expect(34)
      self.Expression()
      if (self.la.kind == 34):
         self.Get( )
         self.Expression()
      self.Expect(29)

   def RobotLook( self ):
      if self.StartOf(9):
         self.Look()
      elif self.la.kind == 53:
         self.LookStmt()
      else:
         self.SynErr(100)

   def RobotPaint( self ):
      if self.StartOf(10):
         self.Paint()
      elif self.la.kind == 62:
         self.PaintStmt()
      else:
         self.SynErr(101)

   def RobotWall( self ):
      if self.StartOf(11):
         self.Wall()
      elif self.la.kind == 67:
         self.WallStmt()
      else:
         self.SynErr(102)

   def RobotMove( self ):
      if self.la.kind == 68 or self.la.kind == 69:
         self.Move()
      elif self.la.kind == 70:
         self.MoveStmt()
      else:
         self.SynErr(103)

   def Look( self ):
      if self.la.kind == 46:
         self.Get( )
      elif self.la.kind == 47:
         self.Get( )
      elif self.la.kind == 48:
         self.Get( )
      elif self.la.kind == 49:
         self.Get( )
      elif self.la.kind == 50:
         self.Get( )
      elif self.la.kind == 51:
         self.Get( )
      elif self.la.kind == 52:
         self.Get( )
      else:
         self.SynErr(104)

   def LookStmt( self ):
      self.Expect(53)
      self.Expect(28)
      self.Expression()
      self.Expect(29)

   def Paint( self ):
      if self.la.kind == 54:
         self.Get( )
      elif self.la.kind == 55:
         self.Get( )
      elif self.la.kind == 56:
         self.Get( )
      elif self.la.kind == 57:
         self.Get( )
      elif self.la.kind == 58:
         self.Get( )
      else:
         self.SynErr(105)
      self.Expect(45)
      if self.la.kind == 59:
         self.Get( )
      elif self.la.kind == 60:
         self.Get( )
      elif self.la.kind == 61:
         self.Get( )
      else:
         self.SynErr(106)

   def PaintStmt( self ):
      self.Expect(62)
      self.Expect(28)
      self.Expression()
      self.Expect(34)
      self.Expression()
      self.Expect(29)

   def Wall( self ):
      if self.la.kind == 63:
         self.Get( )
      elif self.la.kind == 64:
         self.Get( )
      elif self.la.kind == 65:
         self.Get( )
      elif self.la.kind == 66:
         self.Get( )
      else:
         self.SynErr(107)

   def WallStmt( self ):
      self.Expect(67)
      self.Expect(28)
      self.Expression()
      self.Expect(29)

   def Move( self ):
      if self.la.kind == 68:
         self.Get( )
      elif self.la.kind == 69:
         self.Get( )
      else:
         self.SynErr(108)

   def MoveStmt( self ):
      self.Expect(70)
      self.Expect(28)
      self.Expression()
      self.Expect(29)



   def Parse( self, scanner ):
      self.scanner = scanner
      self.la = Token( )
      self.la.val = u''
      self.Get( )
      self.RoboParl()
      self.Expect(0)


   set = [
      [T,x,x,x, x,x,T,T, x,T,T,T, T,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, T,T,T,T, x,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [T,x,x,x, x,x,x,x, x,x,T,T, T,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,T,T, T,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,T,T,T, T,T,T,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,T,T, T,T,T,T, T,T,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,T,T, T,T,T,x, x,x,T,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,T, T,T,T,T, x,x,x,x, x],
      [x,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,T,x,x, x,x,x,T, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, T,x,x,x, x,x,x,x, T,x,T,T, x,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,T,T, T,T,T,T, T,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,T,T, T,T,T,x, x,x,x,x, x,x,x,x, x,x,x,x, x],
      [x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,x, x,x,x,T, T,T,T,x, x,x,x,x, x]

      ]

   errorMessages = {
      
      0 : "EOF expected",
      1 : "idConst expected",
      2 : "intConst expected",
      3 : "doubleConst expected",
      4 : "stringConst expected",
      5 : "\"Program\" expected",
      6 : "\"End\" expected",
      7 : "\"Var\" expected",
      8 : "\"=\" expected",
      9 : "\";\" expected",
      10 : "\"Robot\" expected",
      11 : "\"Int\" expected",
      12 : "\"Double\" expected",
      13 : "\"Bool\" expected",
      14 : "\"String\" expected",
      15 : "\"Void\" expected",
      16 : "\"List\" expected",
      17 : "\">\" expected",
      18 : "\"<\" expected",
      19 : "\">=\" expected",
      20 : "\"<=\" expected",
      21 : "\"==\" expected",
      22 : "\"!=\" expected",
      23 : "\"+\" expected",
      24 : "\"-\" expected",
      25 : "\"*\" expected",
      26 : "\"/\" expected",
      27 : "\"%\" expected",
      28 : "\"(\" expected",
      29 : "\")\" expected",
      30 : "\"True\" expected",
      31 : "\"False\" expected",
      32 : "\"[\" expected",
      33 : "\"]\" expected",
      34 : "\",\" expected",
      35 : "\"Task\" expected",
      36 : "\"If\" expected",
      37 : "\"Else\" expected",
      38 : "\"While\" expected",
      39 : "\"For\" expected",
      40 : "\"In\" expected",
      41 : "\"Print\" expected",
      42 : "\"Read\" expected",
      43 : "\"Return\" expected",
      44 : "\"Break\" expected",
      45 : "\".\" expected",
      46 : "\"lookRight\" expected",
      47 : "\"lookLeft\" expected",
      48 : "\"lookBack\" expected",
      49 : "\"lookNorth\" expected",
      50 : "\"lookEast\" expected",
      51 : "\"lookSouth\" expected",
      52 : "\"lookWest\" expected",
      53 : "\"look\" expected",
      54 : "\"paintFront\" expected",
      55 : "\"paintHere\" expected",
      56 : "\"paintBack\" expected",
      57 : "\"paintRight\" expected",
      58 : "\"paintLeft\" expected",
      59 : "\"Red\" expected",
      60 : "\"Green\" expected",
      61 : "\"Blue\" expected",
      62 : "\"paint\" expected",
      63 : "\"wallFront\" expected",
      64 : "\"wallBack\" expected",
      65 : "\"wallLeft\" expected",
      66 : "\"wallRight\" expected",
      67 : "\"wall\" expected",
      68 : "\"moveFront\" expected",
      69 : "\"moveBack\" expected",
      70 : "\"move\" expected",
      71 : "??? expected",
      72 : "invalid GlobalVars",
      73 : "this symbol not expected in Tasks",
      74 : "this symbol not expected in VarDec",
      75 : "this symbol not expected in VarDec",
      76 : "invalid VarOp",
      77 : "this symbol not expected in VarOp",
      78 : "this symbol not expected in Type",
      79 : "invalid Type",
      80 : "invalid RobotFunc",
      81 : "invalid Factor",
      82 : "invalid Constant",
      83 : "this symbol not expected in Params",
      84 : "invalid Block",
      85 : "this symbol not expected in IfStmt",
      86 : "this symbol not expected in IfStmt",
      87 : "this symbol not expected in IfStmt",
      88 : "this symbol not expected in WhileStmt",
      89 : "this symbol not expected in WhileStmt",
      90 : "this symbol not expected in ForStmt",
      91 : "this symbol not expected in ForStmt",
      92 : "this symbol not expected in WriteStmt",
      93 : "this symbol not expected in WriteStmt",
      94 : "this symbol not expected in ReadStmt",
      95 : "this symbol not expected in ReadStmt",
      96 : "this symbol not expected in ResturnStmt",
      97 : "this symbol not expected in ResturnStmt",
      98 : "this symbol not expected in BreakStmt",
      99 : "this symbol not expected in BreakStmt",
      100 : "invalid RobotLook",
      101 : "invalid RobotPaint",
      102 : "invalid RobotWall",
      103 : "invalid RobotMove",
      104 : "invalid Look",
      105 : "invalid Paint",
      106 : "invalid Paint",
      107 : "invalid Wall",
      108 : "invalid Move",
      }


