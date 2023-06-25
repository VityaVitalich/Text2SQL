class SimplePrompt:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __call__(self, query, **kwargs):
        return [
            {
                "role": "system",
                "content": self.instruction_text,
            },
            {"role": "user", "content": self.few_shot},
            {"role": "user", "content": query},
        ]


class QuestionTableRowsPrompt(SimplePrompt):
    def __call__(self, query, tables, rows, **kwargs):
        tables, rows = self.prepare(tables, rows)
        res = """question: {} {}: {}""".format(
            query, ", ".join(tables), ", ".join(rows)
        )

        return [
            {
                "role": "system",
                "content": self.instruction_text,
            },
            {"role": "user", "content": self.few_shot},
            {"role": "user", "content": res},
        ]

    def prepare(self, tables, rows):
        if isinstance(tables, str):
            tables = [tables]
        if isinstance(rows, str):
            rows = [rows]

        assert isinstance(tables, list), "Passed tables are not List or Str"
        assert isinstance(rows, list), "Passed rows are not List or Str"

        return tables, rows
