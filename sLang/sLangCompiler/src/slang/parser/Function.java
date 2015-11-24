package slang.parser;

import slang.parser.statements.Block;
import slang.parser.statements.VariableDeclaration;

public interface Function
{
	public String getName();
	public VariableDeclaration[] getParameters();
	public Datatype getRetType();
	public Block getBody();
}
