class SimplePrompt:

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __call__(self, query, **kwargs):
        return self._transforms(query)
    
    def _transforms(self, query):
        return self._insert_instructions(self._insert_few_shot(query))

    def _insert_few_shot(self, query):

        if self.few_shot:
            return self.few_shot_text + '\n' + query
        return query

    def _insert_instructions(self, query):

        return self.instruction_text + '\n' + query


class QuestionTableRowsPrompt(SimplePrompt):

    
    def __call__(self, query, tables, rows, **kwargs):

        tables, rows = self.prepare(tables, rows)
        res = """question: {} {}: {}""".format(
                                        query,
                                        ', '.join(tables),
                                        ', '.join(rows)
                                        )
        
        return self._transforms(res)
    
    def prepare(self, tables, rows):

        if isinstance(tables, str):
            tables = [tables]
        if isinstance(rows, str):
            rows = [rows]

        assert isinstance(tables, list), 'Passed tables are not List or Str'
        assert isinstance(rows, list), 'Passed rows are not List or Str'
        
        return tables, rows