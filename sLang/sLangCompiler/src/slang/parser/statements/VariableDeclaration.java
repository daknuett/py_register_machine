package slang.parser.statements;

import slang.parser.Datatype;
import slang.parser.Statement;

public interface VariableDeclaration extends Statement
{
	public Datatype getType();
	public String getName();
}
