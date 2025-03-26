import axios from 'axios'

export const validateAdminToken = async (token) => {
  try {
    const response = await axios.get('http://localhost:5000/auth/own', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data.user.is_admin === true
  } catch (error) {
    return false
  }
} 