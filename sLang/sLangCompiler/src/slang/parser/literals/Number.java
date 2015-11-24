package slang.parser.literals;

import slang.parser.statements.parts.Expression;

public interface Number extends Expression
{
	public int getValue();
}
