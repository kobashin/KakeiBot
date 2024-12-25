# coding: utf-8

"""
    Webhook Type Definition

    Webhook event definition of the LINE Messaging API  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


from __future__ import annotations
import pprint
import re  # noqa: F401
import json
import linebot.v3.webhooks.models


from typing import Union
from pydantic.v1 import BaseModel, Field, StrictStr

class MessageContent(BaseModel):
    """
    MessageContent
    https://developers.line.biz/en/reference/messaging-api/#message-event
    """
    type: StrictStr = Field(..., description="Type")
    id: StrictStr = Field(..., description="Message ID")

    __properties = ["type", "id"]

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    # JSON field name that stores the object type
    __discriminator_property_name = 'type'

    # discriminator mappings
    __discriminator_value_class_map = {
        'audio': 'AudioMessageContent',
        'file': 'FileMessageContent',
        'image': 'ImageMessageContent',
        'location': 'LocationMessageContent',
        'sticker': 'StickerMessageContent',
        'text': 'TextMessageContent',
        'video': 'VideoMessageContent'
    }

    @classmethod
    def get_discriminator_value(cls, obj: dict) -> str:
        """Returns the discriminator value (object type) of the data"""
        discriminator_value = obj[cls.__discriminator_property_name]
        if discriminator_value:
            return cls.__discriminator_value_class_map.get(discriminator_value)
        else:
            return None

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Union(AudioMessageContent, FileMessageContent, ImageMessageContent, LocationMessageContent, StickerMessageContent, TextMessageContent, VideoMessageContent):
        """Create an instance of MessageContent from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> Union(AudioMessageContent, FileMessageContent, ImageMessageContent, LocationMessageContent, StickerMessageContent, TextMessageContent, VideoMessageContent):
        """Create an instance of MessageContent from a dict"""
        # look up the object type based on discriminator mapping
        object_type = cls.get_discriminator_value(obj)
        if object_type:
            klass = getattr(linebot.v3.webhooks.models, object_type)
            return klass.from_dict(obj)
        else:
            raise ValueError("MessageContent failed to lookup discriminator value from " +
                             json.dumps(obj) + ". Discriminator property name: " + cls.__discriminator_property_name +
                             ", mapping: " + json.dumps(cls.__discriminator_value_class_map))

