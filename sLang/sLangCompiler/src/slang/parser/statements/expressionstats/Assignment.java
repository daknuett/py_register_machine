package slang.parser.statements.expressionstats;

import slang.parser.Variable;
import slang.parser.statements.ExpressionStatement;
import slang.parser.statements.parts.Expression;

public interface Assignment extends ExpressionStatement
{
	public Variable getTarget();
	public Expression getValue();
}
