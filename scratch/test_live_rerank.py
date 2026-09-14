import urllib.request
import json

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/agent/stream',
    data=json.dumps({
        'conversation_id': 'test_rerank_val',
        'messages': [{'role': 'user', 'content': 'My package shows delivered yesterday but I never received it. Carrier was USPS and I already checked with my neighbors.'}]
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

resp = urllib.request.urlopen(req)
rerank_event = None
for line in resp:
    line_str = line.decode('utf-8').strip()
    if line_str.startswith('data: '):
        ev = json.loads(line_str[6:])
        if ev.get('type') == 'rerank':
            rerank_event = ev
            break

if rerank_event:
    print('RERANK EVENT RECEIVED:')
    for c in rerank_event['retrieved_evidence']:
        print(f"#{c.get('rank')} | Case: {c.get('case_id')} | Sem: {c.get('semantic_score')} | Lex: {c.get('lexical_score')} | Intent: {c.get('intent_score')} | Area: {c.get('area_score')} | State: {c.get('state_score')} | ActionUseful: {c.get('action_usefulness')} | Final: {c.get('final_score')}")
else:
    print('NO RERANK EVENT FOUND')
