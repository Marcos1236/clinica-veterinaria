import json
from channels.generic.websocket import AsyncWebsocketConsumer


connected_users = {}
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'
        self.user_id = self.scope['user'].dni

        if self.chat_id not in connected_users:
            connected_users[self.chat_id] = set()

        connected_users[self.chat_id].add(self.user_id)

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        connected_users[self.chat_id].discard(self.user_id)

        if not connected_users[self.chat_id]:
            del connected_users[self.chat_id]

        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender'] 
        recipient = data['recipient']  

        if message == "new_chat":
            await self.channel_layer.group_send(
                f'chat_{recipient}', 
                {
                    'type': 'new_chat', 
                    'client_name': sender,  
                    'client_id': self.chat_id,  
                }
            )
        elif message == "check_connection":

            if len(connected_users[recipient]) > 1:
                success = True
            else:
                success = False
            await self.channel_layer.group_send(
                f'chat_{recipient}', 
                {
                    'type': 'check_connection',  
                    'success': success,
                }
            )
        elif message == "close_connection":
            await self.channel_layer.group_send(
                f'chat_{recipient}', 
                {
                    'type': 'close_connection',  
                }
            )
        else:
            await self.channel_layer.group_send(
                f'chat_{recipient}', 
                {
                    'type': 'chat_message',  
                    'message': message,
                    'sender': sender,
                }
            )

        

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
        }))

    async def new_chat(self, event):
        client_name = event['client_name']
        client_id = event['client_id']

        await self.send(text_data=json.dumps({
            'type': 'new_chat',
            'client_name': client_name,
            'client_id': client_id,
        }))

    async def check_connection(self,event):
        success = event['success']
        await self.send(text_data=json.dumps({
            'type': 'check_connection',
            'success': success
        }))

    async def close_connection(self,event):
        await self.send(text_data=json.dumps({
            'type': 'close_connection',
        }))
