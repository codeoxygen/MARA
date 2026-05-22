import { PlusOutlined } from '@ant-design/icons'
import Button from './Button'

export default function NewChatButton({ onClick, disabledStatus }) {
  return (
    <Button variant="primary" size="sm" onClick={onClick} disabled={disabledStatus}>
      <PlusOutlined />
      New
    </Button>
  )
}
