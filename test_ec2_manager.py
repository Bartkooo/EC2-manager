from unittest.mock import mock_open, patch
import json


def save_instance_id(instance_id):
    with open('instance_id.json', 'w') as f:
        json.dump({'instance_id': instance_id}, f)


def test_save_instance_id():
    instance_id = "x-0982345ghklsg09144hd"
    expected_content = json.dumps({'instance_id': instance_id})

    mocked_open = mock_open()
    with patch("builtins.open", mocked_open) as mocked_file:
        save_instance_id(instance_id)

        mocked_file.assert_called_once_with('instance_id.json', 'w')

        file_handle = mocked_file()
        write_calls = file_handle.write.call_args_list

        written_content = ''.join(call.args[0] for call in write_calls)

        assert written_content == expected_content
