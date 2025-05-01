import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Switch,
  FormControlLabel,
  TextField,
  Alert,
} from '@mui/material';
import axios from 'axios';

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState({
    username: '',
    email: '',
    mfa_enabled: false,
    phone_number: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/api/profile/', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setProfile(response.data);
    } catch (err) {
      setError('Failed to fetch profile');
    }
  };

  const handleMfaToggle = async () => {
    try {
      const response = await axios.post(
        '/api/toggle-mfa/',
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      setProfile({ ...profile, mfa_enabled: response.data.mfa_enabled });
      setSuccess('MFA settings updated successfully');
    } catch (err) {
      setError('Failed to update MFA settings');
    }
  };

  const handlePhoneUpdate = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        '/api/update-phone/',
        { phone_number: profile.phone_number },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      setProfile({ ...profile, phone_number: response.data.phone_number });
      setSuccess('Phone number updated successfully');
    } catch (err) {
      setError('Failed to update phone number');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Profile
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle1">Username: {profile.username}</Typography>
            <Typography variant="subtitle1">Email: {profile.email}</Typography>
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={profile.mfa_enabled}
                onChange={handleMfaToggle}
                color="primary"
              />
            }
            label="Enable Two-Factor Authentication"
          />
          <form onSubmit={handlePhoneUpdate}>
            <TextField
              margin="normal"
              fullWidth
              label="Phone Number"
              value={profile.phone_number}
              onChange={(e) =>
                setProfile({ ...profile, phone_number: e.target.value })
              }
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 2, mb: 2 }}
            >
              Update Phone Number
            </Button>
          </form>
          <Button
            fullWidth
            variant="outlined"
            color="secondary"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default Profile; 