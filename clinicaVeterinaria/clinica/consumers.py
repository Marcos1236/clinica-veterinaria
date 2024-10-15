import json
from channels.generic.websocket import AsyncWebsocketConsumer



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender'] 
        recipient = data['recipient']  
        print(data)

        # Enviar el mensaje al grupo del veterinario
        await self.channel_layer.group_send(
            f'chat_{recipient}',  # Grupo único para cada veterinario
            {
                'type': 'chat_message',  
                'message': message,
                'sender': sender,
            }
        )

        # Notificar al veterinario que ha comenzado un nuevo chat
        await self.channel_layer.group_send(
            f'chat_{recipient}', 
            {
                'type': 'new_chat', 
                'client_name': sender,  
                'client_id': self.chat_id,  
            }
        )

    # Método para manejar los mensajes de chat y enviarlos al WebSocket
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Enviar el mensaje al frontend en formato JSON
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    # Método para notificar al veterinario sobre un nuevo chat
    async def new_chat(self, event):
        client_name = event['client_name']
        client_id = event['client_id']

        # Enviar la notificación de nuevo chat al frontend
        await self.send(text_data=json.dumps({
            'type': 'new_chat',
            'client_name': client_name,
            'client_id': client_id,
        }))
