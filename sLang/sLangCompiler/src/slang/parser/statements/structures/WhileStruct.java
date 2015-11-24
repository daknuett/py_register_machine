package slang.parser.statements.structures;

import slang.parser.Statement;
import slang.parser.statements.Structure;
import slang.parser.statements.parts.Expression;

public interface WhileStruct extends Structure
{
	public Expression getCondition();
	public Statement getBody();
}
