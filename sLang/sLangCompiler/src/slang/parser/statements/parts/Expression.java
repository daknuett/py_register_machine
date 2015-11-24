package slang.parser.statements.parts;

public interface Expression
{
	public BinaryOperator getOperation();
	public Expression getSecondExpression();
	
	public enum BinaryOperator
	{
		PLUS, MINUS, MULTIPLY, DIVIDE, AND, XOR, OR, GREATER, LESS, EQUALS
	}
}
