#!/usr/local/bin/python
def main():
    reactions = [
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'No reaction', 'face_uuid': '6eff665c0cf24e09a6d180f1e90077fb', 'parent_uuid': '34316fff4388494fb08193502fae939a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Лариса', 'common_param': {'x': 123}, 'param': {'y': 456}},
        {'point_id': 5, 'point_name': 'Sezon', 'group_name': 'Співробітники', 'reaction_name': 'No reaction', 'face_uuid': 'c3664862f46b485fbb04e2b4d6e5c8f3', 'parent_uuid': '65d25cd148e6434d8c8d3820168e926a', 'ts': '2025-12-26T15:12:10.089620', 'name': 'Адель', 'common_param': {'x': 123}, 'param': {'y': 456}},
    ]
    make_reaction(None, reactions)

def make_reaction(cursor, reactions):
#    for reaction in reactions:
#        print(reaction)
#        print()

    return 'Ok'

if __name__ == "__main__":
    main()
