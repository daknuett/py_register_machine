package slang.parser.statements.structures;

import slang.parser.Statement;
import slang.parser.statements.parts.Expression;

public interface IfStruct
{
	public Expression getCondition();
	public Statement getTrueBody();
	public Statement getFalseBody();
}
