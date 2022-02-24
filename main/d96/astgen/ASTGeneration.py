from D96Visitor import D96Visitor
from D96Parser import D96Parser
from AST import *
# from main.d96.utils.AST import *
from functools import reduce

class ASTGeneration(D96Visitor):
    def visitProgram(self, ctx: D96Parser.ProgramContext):
        return Program(self.visit(ctx.decls()))

    def visitDecls(self, ctx: D96Parser.DeclsContext):
        if ctx.getChildCount()==1:
            return self.visit(ctx.class_decl())
        return self.visit(ctx.class_decl()) +self.visit(ctx.decls())

    def visitClass_decl(self, ctx: D96Parser.Class_declContext):
        if ctx.COLON():
            classname=Id(str(ctx.ID(0).getText()))
            parentname=Id(str(ctx.ID(1).getText()))
            if ctx.class_bodys():
                return [ClassDecl(classname,self.visit(ctx.class_bodys()),parentname)]
            return [ClassDecl(classname,[],parentname)]
        else:
            classname=Id(str(ctx.ID(0).getText()))
            if ctx.class_bodys():
                return [ClassDecl(classname,self.visit(ctx.class_bodys()),None)]
            return [ClassDecl(classname,[],None)]
            
        # if ctx.class_bodys():
        #     memlist=self.visit(ctx.class_bodys())
        #     if ctx.COLON():
        #         parentname=self.visit(ctx.ID(1).getText())
        #         return [ClassDecl(classname,memlist,parentname)] +print("213")
        #     return [ClassDecl(classname,memlist,None)]+print("21345")
        # return [ClassDecl(classname,[],None)]+print("21345")
            
    def visitClass_bodys(self, ctx: D96Parser.Class_bodysContext):
        if ctx.getChildCount()==1:
            return self.visit(ctx.class_body())
        return self.visit(ctx.class_body()) +self.visit(ctx.class_bodys())

    def visitClass_body(self, ctx: D96Parser.Class_bodyContext):
        if ctx.attribute_decl():
            return self.visit(ctx.attribute_decl())
        return self.visit(ctx.method_decl())

    def visitTyp_name(self, ctx: D96Parser.Typ_nameContext): pass

    def visitVariable_decl(self, ctx: D96Parser.Variable_declContext):
        variables=self.visit(ctx.list_name())
        varType=self.visit(ctx.typ_var())
        
        if ctx.list_exp():
            varInit=self.visit(ctx.list_exp())
            
            return list(map(lambda x,y:VarDecl(Id(x),varType,y),variables,varInit ))
        if type(varType) is ClassType:
            return list(map(lambda a:VarDecl(Id(a),varType,NullLiteral()),variables))
        return list(map(lambda x:VarDecl(Id(x),varType,None),variables))
        
    def visitConst_decl(self, ctx: D96Parser.Const_declContext):
        variables=self.visit(ctx.list_name())
        varType=self.visit(ctx.typ_var())
        
        if ctx.list_exp():
            varInit=self.visit(ctx.list_exp())
            
            return list(map(lambda a,b:ConstDecl(Id(a),varType,b),variables,varInit ))
        if type(varType) is ClassType:
            return list(map(lambda a:ConstDecl(Id(a),varType,NullLiteral()),variables))
        return list(map(lambda a:ConstDecl(Id(a),varType,None),variables))

    def visitAttribute_decl(self, ctx: D96Parser.Attribute_declContext): 
        # if ctx.variable_decl():
        #     name=str(self.visit(ctx.variable_decl().variable.getText()))
        #     if "$" in name:
        #         return [AttributeDecl(Static(),self.visit(ctx.variable_decl()))]
        #     else:
        #         return [AttributeDecl(Instance(),self.visit(ctx.variable_decl()))]
        # else:
        #     name=str(self.visit(ctx.const_decl().variable.getText()))
        #     if "$" in name:
        #         return [AttributeDecl(Static(),self.visit(ctx.const_decl()))]
        #     else:
        #         return [AttributeDecl(Instance(),self.visit(ctx.const_decl()))]
        res=[]
        if ctx.variable_decl():
            for x in self.visit(ctx.variable_decl()):
                if "$" in x.variable.name:
                    
                    res+= [AttributeDecl(Static(),x)]
                else:
                    res+= [AttributeDecl(Instance(),x)]
            return res
        else:
            for x in self.visit(ctx.const_decl()):
                
                if "$" in x.constant.name:
                    
                    res+= [AttributeDecl(Static(),x)]
                else:
                    res+= [AttributeDecl(Instance(),x)]
            return res

    def visitList_name(self, ctx: D96Parser.List_nameContext):
        if ctx.getChildCount()==1:
            if ctx.Dollar_id():
                return [ctx.Dollar_id().getText()]
            elif ctx.ID():
                return [ctx.ID().getText()]
        else:
            if ctx.Dollar_id():
                return [ctx.Dollar_id().getText()]+ self.visit(ctx.list_name())
            elif ctx.ID():
                return [ctx.ID().getText()]+ self.visit(ctx.list_name())
            
    def visitName_att(self, ctx: D96Parser.Name_attContext):
        if ctx.ID():
            return Id(ctx.ID().getText())
        return Id(ctx.Dollar_id().getText())

    # def visitOptionally(self, ctx: D96Parser.OptionallyContext): pass

    def visitList_exp(self, ctx: D96Parser.List_expContext):
        if ctx.getChildCount()==1:
            if ctx.expr():
                return [self.visit(ctx.expr())]
        return [self.visit(ctx.expr())] +self.visit(ctx.list_exp())

    def visitMethod_decl(self, ctx: D96Parser.Method_declContext):
        if ctx.ID():
            name=Id(str(ctx.ID().getText()))
            body=self.visit(ctx.block_stm())
            if ctx.parameter():
                param=self.visit(ctx.parameter())
                return [MethodDecl(name,Instance(),param,body)]
            return [MethodDecl(name,Instance(),[],body)]
        elif ctx.Dollar_id():
            name=Id(str(ctx.ID().getText()))
            if ctx.parameter():
                param=self.visit(ctx.parameter())
                return [MethodDecl(name,Static(),param,body)]
            return [MethodDecl(name,Static(),[],body)]
        elif ctx.destructor():
            return self.visit(ctx.destructor())
        elif ctx.constructor():
            return self.visit(ctx.constructor())
    def visitParameter(self, ctx: D96Parser.ParameterContext): 
        
        variable=self.visit(ctx.identifer_list())
        varType=self.visit(ctx.typ_var())
        res=[]
        for x in variable:
            res+=[VarDecl(x,varType)]
        if ctx.parameter():
            return res + self.visit(ctx.parameter())
        return res

    def visitIdentifer_list(self, ctx: D96Parser.Identifer_listContext):
        if ctx.identifer_list():
            return [self.visit(ctx.name_att())]+self.visit(ctx.identifer_list())
        return [self.visit(ctx.name_att())]
    def visitConstructor(self, ctx: D96Parser.ConstructorContext): 
        body=self.visit(ctx.block_stm())
        if ctx.parameter():
            param=[self.visit(ctx.parameter())]
            return [MethodDecl(ctx.CONSTRUCTOR().getText(),Instance(),param,body)]
        else:
            return [MethodDecl(ctx.CONSTRUCTOR().getText(),Instance(),[],body)]
    def visitDestructor(self, ctx: D96Parser.DestructorContext):
        return [MethodDecl(ctx.DESTRUCTOR().getText(),Instance(),[],self.visit(ctx.block_stm()))]

    # def visitVariable_decl(self, ctx: D96Parser.Variable_declContext): pass

    def visitBlock_stm(self, ctx: D96Parser.Block_stmContext): 
        if ctx.statements():
            stm=self.visit(ctx.statements())
            return Block(stm)
        return Block([])
        
    def visitStatement(self, ctx: D96Parser.StatementContext):
        if ctx.variable_decl():
            res=[]
            for x in self.visit(ctx.variable_decl()):
                res+=[x]
            return res
        elif ctx.foreach_stmt():
            return [self.visit(ctx.foreach_stmt())]
        elif ctx.assignment_statement():
            return [self.visit(ctx.assignment_statement())]  
        elif ctx.if_statement():
            return [self.visit(ctx.if_statement())]
        elif ctx.break_stmt():
            return [self.visit(ctx.break_stmt())]
        elif ctx.cont_stmt():
            return [self.visit(ctx.cont_stmt())]
        elif ctx.return_stmt():
            return [self.visit(ctx.return_stmt())]
        elif ctx.block_stm():
            return [self.visit(ctx.block_stm())]
        elif ctx.member_access():
            return [self.visit(ctx.member_access())]

    def visitStatements(self, ctx: D96Parser.StatementsContext):
        if ctx.getChildCount()==1:
            return self.visit(ctx.statement())
        return self.visit(ctx.statement())+self.visit(ctx.statements())
    def visitIndex_operators(self, ctx: D96Parser.Index_operatorsContext):
        if ctx.index_operators():
            return [self.visit(ctx.expr())]+self.visit(ctx.index_operators())
        else:

            return [self.visit(ctx.expr())]

    def visitFunc_call(self, ctx: D96Parser.Func_callContext): pass

    def visitExpr(self, ctx: D96Parser.ExprContext):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr1(0))
        op=str(ctx.getChild(1).getText())
        left=self.visit(ctx.expr1(0))
        right=self.visit(ctx.expr1(1))
        return BinaryOp(op,left,right)

    def visitExpr1(self, ctx: D96Parser.Expr1Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr2(0))
        op=ctx.getChild(1).getText()
        left=self.visit(ctx.expr2(0))
        right=self.visit(ctx.expr2(1))
        return BinaryOp(op,left,right)

    def visitExpr2(self, ctx: D96Parser.Expr2Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr3())
        op=ctx.getChild(1).getText()
        left=self.visit(ctx.expr2())
        right=self.visit(ctx.expr3())
        return BinaryOp(op,left,right)

    def visitExpr3(self, ctx: D96Parser.Expr3Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr4())
        op=ctx.getChild(1).getText()
        left=self.visit(ctx.expr3())
        right=self.visit(ctx.expr4())
        return BinaryOp(op,left,right)

    def visitExpr4(self, ctx: D96Parser.Expr4Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr5())
        op=ctx.getChild(1).getText()
        left=self.visit(ctx.expr4())
        right=self.visit(ctx.expr5())
        return BinaryOp(op,left,right)

    def visitExpr5(self, ctx: D96Parser.Expr5Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr6())
        op=ctx.getChild(0).getText()
        body=self.visit(ctx.expr5())
        return UnaryOp(op,body)

    def visitExpr6(self, ctx: D96Parser.Expr6Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr7())
        op=ctx.getChild(0).getText()
        body=self.visit(ctx.expr6())
        return UnaryOp(op,body)

    def visitExpr7(self, ctx: D96Parser.Expr7Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr8())
        arr=self.visit(ctx.expr7())
        idx=self.visit(ctx.index_operators())
        return ArrayCell(arr,idx)

    def visitExpr8(self, ctx: D96Parser.Expr8Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr9())
        obj=self.visit(ctx.expr8())
        fieldname=Id(ctx.ID().getText())
        if ctx.getChildCount()==3:
            return FieldAccess(obj,fieldname)
        else:
            if ctx.list_exp():
                param=self.visit(ctx.list_exp())
                return CallExpr(obj,fieldname,param)
            else:
                return CallExpr(obj,fieldname,[])



    def visitExpr9(self, ctx: D96Parser.Expr9Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr10())
        obj=Id(ctx.ID().getText())
        fieldname=Id(ctx.ID().getText())
        if ctx.getChildCount()==3:
            return FieldAccess(obj,fieldname)
        else:
            if ctx.list_exp():
                param=self.visit(ctx.list_exp())
                return CallExpr(obj,fieldname,param)
            else:
                return CallExpr(obj,fieldname,[])

    def visitExpr10(self, ctx: D96Parser.Expr10Context):
        if ctx.getChildCount()==1:
            return self.visit(ctx.expr11())
        classname=Id(ctx.ID().getText())
        
        if ctx.list_exp():
            param=self.visit(ctx.list_exp())
            return NewExpr(classname,param)
        return NewExpr(classname,[])

    def visitExpr11(self, ctx: D96Parser.Expr11Context):
        if ctx.getChildCount()==3:
            return self.visit(ctx.expr())
        else:
            return self.visit(ctx.operand())
            
    def visitMember_access(self, ctx: D96Parser.Member_accessContext):
        if ctx.expr8():
            return self.visit(ctx.expr8())
        return self.visit(ctx.expr9())

    def visitOperand(self, ctx: D96Parser.OperandContext):
        if ctx.literal():
            return self.visit(ctx.literal())
        elif ctx.name_att():
            return self.visit(ctx.name_att())
        elif ctx.NULL():
            return NullLiteral()
        elif ctx.SELF():
            
            return SelfLiteral()
    def visitLiteral(self, ctx: D96Parser.LiteralContext):
        if ctx.INTLIT():
            return IntLiteral(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            return FloatLiteral(float(ctx.FLOATLIT().getText()))
        elif ctx.STRINGLIT():
            return StringLiteral(ctx.STRINGLIT().getText())
        elif ctx.boolit():
            return BooleanLiteral(True if str(ctx.boolit().getText())=='True' else False)
        elif ctx.arraylit():
            return self.visit(ctx.arraylit())

    def visitAssignment_statement(self, ctx: D96Parser.Assignment_statementContext):
        lhs=self.visit(ctx.expr(0))
        rhs=self.visit(ctx.expr(1))
        return Assign(lhs,rhs)

    def visitIf_statement(self, ctx: D96Parser.If_statementContext):
        expr=self.visit(ctx.expr())
        thenStm=self.visit(ctx.block_stm())
        if ctx.elseStmt():
            
            elseStm=self.visit(ctx.elseStmt())
            # for x in elseStm:
            #     if x.getChildCount():
            
            return If(expr,thenStm,elseStm)
        return If(expr,thenStm,None)

    def visitElseStmt(self, ctx: D96Parser.ElseStmtContext):
       
        if ctx.elseStmt():
            expr=self.visit(ctx.elif_stm())
            elseStm=self.visit(ctx.elseStmt())
            
            return If(expr[0],expr[1],elseStm)
        elif ctx.else_stm():
            return self.visit(ctx.else_stm())
        else:
            expr=self.visit(ctx.elif_stm())
            return If(expr[0],expr[1],None)
    
    def visitElif_stm(self, ctx: D96Parser.Elif_stmContext):
        expr=self.visit(ctx.expr())
        thenStm=self.visit(ctx.block_stm())
        return expr,thenStm

    # def visitStmt_if(self, ctx: D96Parser.Stmt_ifContext): 
    #     expr=self.visit(ctx.expr())
    #     stm=self.visit(ctx.block_stm())
    #     return expr,stm

    def visitElse_stm(self, ctx: D96Parser.Else_stmContext):
        
        return self.visit(ctx.block_stm())
        
        
    def visitForeach_stmt(self, ctx: D96Parser.Foreach_stmtContext):
        name= Id(str(ctx.ID().getText()))
        expr1=IntLiteral(int(ctx.INTLIT(0).getText()))
        expr2=IntLiteral(int(ctx.INTLIT(1).getText()))
        loop=self.visit(ctx.block_stm())
        if ctx.INTLIT(2):
            expr3=IntLiteral(int(ctx.INTLIT(2).getText()))
            return For(name,expr1,expr2,loop,expr3)
        return For(name,expr1,expr2,loop,None)
    def visitBreak_stmt(self, ctx: D96Parser.Break_stmtContext):
        return Break()

    def visitCont_stmt(self, ctx: D96Parser.Cont_stmtContext):
        return Continue()

    def visitCall_stmt(self, ctx: D96Parser.Call_stmtContext): pass

    def visitReturn_stmt(self, ctx: D96Parser.Return_stmtContext):
        if ctx.expr():
            return Return(self.visit(ctx.expr()))
        return Return(None)

    def visitTyp_var(self, ctx: D96Parser.Typ_varContext):
        if ctx.INT():
            return IntType()
        elif ctx.FLOAT():
            return FloatType()
        elif ctx.BOOLEAN():
            return BoolType()
        elif ctx.STRING():
            return StringType()
        elif ctx.array():
            return self.visit(ctx.array())
        elif ctx.class_type():
            return ClassType(self.visit(ctx.class_type()))
    def visitClass_type(self, ctx: D96Parser.Class_typeContext):
        return ctx.ID().getText()
    def visitArray(self, ctx: D96Parser.ArrayContext):
        eleType=self.visit(ctx.typ_var())
        size=IntLiteral(int(ctx.INTLIT().getText()))
        return ArrayType(size,eleType)
    def visitArraylit(self, ctx: D96Parser.ArraylitContext):
        
        return self.visit(ctx.getChild(0))

    def visitIar(self, ctx: D96Parser.IarContext):
        if [ctx.getChild(2)]==[ctx.RP()]:
            return []
        return ArrayLiteral(self.visit(ctx.getChild(2)))
    def visitAints(self, ctx: D96Parser.AintsContext): 
        if ctx.getChildCount()==1:
            
            return [IntLiteral(int(ctx.INTLIT().getText()))]
        
        return [IntLiteral(int(ctx.INTLIT().getText()))]+ self.visit(ctx.aints())

    def visitAfloats(self, ctx: D96Parser.AfloatsContext):
        if ctx.getChildCount()==1:
            return [FloatLiteral(float(ctx.FLOATLIT().getText()))]
        return [FloatLiteral(float(ctx.FLOATLIT().getText()))] + self.visit(ctx.afloats())


    def visitAstrings(self, ctx: D96Parser.AstringsContext): 
        if ctx.getChildCount()==1:
            return [StringLiteral(ctx.STRINGLIT().getText())]
        return [StringLiteral(ctx.STRINGLIT().getText())] + self.visit(ctx.astrings())

    def visitAsbools(self, ctx: D96Parser.AsboolsContext):
        if ctx.getChildCount()==1:
            return [BooleanLiteral(True if ctx.boolit().getText()=='True' else False)]
        return [BooleanLiteral(True if str(ctx.boolit().getText())=='True' else False)] +self.visit(ctx.asbools())

    def visitMar(self, ctx: D96Parser.MarContext):
        return ArrayLiteral(self.visit(ctx.marraylists()))

    def visitMarraylists(self, ctx: D96Parser.MarraylistsContext):
        if ctx.getChildCount()==1:
            return [self.visit(ctx.iar())]
        return [self.visit(ctx.iar())] + self.visit(ctx.marraylists())
