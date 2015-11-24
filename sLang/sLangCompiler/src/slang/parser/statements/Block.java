package slang.parser.statements;

import slang.parser.Statement;

public interface Block extends Statement
{
	public Statement[] getStatements();
}
