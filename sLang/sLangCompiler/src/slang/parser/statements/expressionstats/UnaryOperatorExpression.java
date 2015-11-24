package slang.parser.statements.expressionstats;

import slang.parser.Variable;
import slang.parser.statements.ExpressionStatement;
import slang.parser.statements.parts.Expression;

public interface UnaryOperatorExpression extends ExpressionStatement, Expression
{
	public Variable getVariable();
	public UnaryOperator getOperator();
	
	public enum UnaryOperator
	{
		INCREMENT_PRE, INCREMENT_POST, DECREMENT_PRE, DECREMENT_POST
	}
}
