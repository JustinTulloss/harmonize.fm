# The mother of all file actions
# Does all the ugly stuff, starts threads, defines queues, eats babies, etc.
from amqplib import client_0_8 as amqp
import logging
import cjson
import os
from ..configuration import config

log = logging.getLogger(__name__)

class BaseAction(object):

    def __init__(self, cleanup=None, consuming=None):
        self.exchange = 'fileprocess'
        self.consuming = consuming
        self._connection = amqp.Connection(
                host = "localhost:5672",
                userid = "guest",
                password = "guest",
                virtual_host = config['amqp_vhost'],
                insist = False)
        self._channel = self._connection.channel()
        self.message_key = self.__class__.__name__
        self._channel.queue_declare(
                queue = self.message_key,
                durable = True,
                exclusive = False,
                auto_delete = False)

    def _loop(self):
        while(self._running):
            message = self._channel.basic_get(queue = self.message_key)
            if message:
                self._message_received(message)
            else:
                self._channel.wait()
        self.stop()

    def _message_received(self, message):
        received_file = cjson.decode(message.body, all_unicode=True)
        log.info('received %s' % message.body)
        self._channel.basic_ack(message.delivery_tag)
        try:
            processed_file = self.process(received_file)
        except Exception, e:
            log.exception(e)
            self.failure(received_file)
            processed_file = False

        if processed_file:
            self._channel.basic_publish(
                self._file_to_message(processed_file),
                exchange = self.exchange,
                routing_key = self.message_key)
        else:
            log.warn('Message failed. Not sure what happens now.')

    def _file_to_message(self, file):
        return amqp.Message(
            cjson.encode(file),
            delivery_mode = 2) # persistent messages for now

    def stop(self):
        log.info('Stopping')
        self._channel.basic_cancel(self.message_key)
        self._channel.close()
        self._connection.close()

    def start(self):
        self._channel.queue_bind(
            queue = self.message_key,
            exchange = self.exchange,
            routing_key = self.consuming)
        self._channel.basic_consume(
            queue = self.message_key,
            no_ack = False,
            callback = self._message_received,
            consumer_tag = self.message_key)
        self._running = True
        self._loop()

    def failure(self, file):
        if file.get('failures')>3:
            file['msg'] = "Upload had an unexpected failure"
            file['na']  = na.FAILURE
            self.cleanup(file)
        else:
            if file.has_key('failures'):
                file['failures'] = file['failures']+1
            else:
                file['failures'] = 0
                self._channel.basic_publish(
                        self._file_to_message(file),
                        exchange = self.exchange,
                        routing_key = "failure")

    def cleanup(self, file):
        self._channel.basic_publish(
                self._file_to_message(file),
                exchange = self.exchange,
                routing_key = "cleanup")

    def can_skip(self, nf):
        """
        For actions like Transcoder that certain files can skip completely
        """
        return False

    def process(self, nf):
        """
        Override this function
        """
        return nf
