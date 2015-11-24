package slang.parser;

import slang.parser.statements.parts.Expression;

public interface Variable extends Expression
{
	public String getName();
	public Datatype getType();
}
