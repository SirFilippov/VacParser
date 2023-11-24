from parsers.hh import Parser as HH_Parser


class Manager:
    def __init__(self):
        self.parsers = (
            HH_Parser(),
        )

    def generate(self):
        api = {
            'data': {},
            'errors': [],
        }

        for parser in self.parsers:
            parser_data = parser.generate()
            api['data'].update(parser_data['data'])
            if parser_data['errors']:
                errors = f'{parser_data["name"]}: {parser_data["name"]}'
                api['errors'].append(errors)

        api['errors'] = '\n'.join(api['errors'])

        return api


if __name__ == "__main__":
    print(Manager().generate())
