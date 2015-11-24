package slang.parser.statements.expressionstats;

import slang.parser.Function;
import slang.parser.statements.ExpressionStatement;
import slang.parser.statements.parts.Expression;

public interface Functioncall extends ExpressionStatement, Expression
{
	public Function getFunction();
	public Expression[] getParameters();
}
