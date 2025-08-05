import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useStripe, useElements, CardElement } from '@stripe/react-stripe-js';
import styled from 'styled-components';
import toast from 'react-hot-toast';
import axios from 'axios';

const Container = styled.div`
  max-width: 600px;
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h1`
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 0.5rem;
  text-align: center;
`;

const Subtitle = styled.p`
  color: #666;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.1rem;
`;

const PluginInfo = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  text-align: center;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const Label = styled.label`
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
`;

const Input = styled.input`
  padding: 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
  
  &.error {
    border-color: #ff6b6b;
  }
`;

const Select = styled.select`
  padding: 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  font-size: 1rem;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #667eea;
  }
`;

const PricingCards = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
`;

const PricingCard = styled.div`
  border: 2px solid ${props => props.selected ? '#667eea' : '#e1e8ed'};
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
  background: ${props => props.selected ? '#f8f9ff' : 'white'};
  
  &:hover {
    border-color: #667eea;
  }
`;

const CardWrapper = styled.div`
  border: 2px solid #e1e8ed;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1.2rem 2rem;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ErrorText = styled.span`
  color: #ff6b6b;
  font-size: 0.8rem;
`;

const PRICING_PLANS = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    features: ['500MB Storage', '5K API calls/month', 'Basic support']
  },
  {
    id: 'starter',
    name: 'Light User',
    price: 3.99,
    features: ['2GB Storage', '25K API calls/month', 'Email support']
  },
  {
    id: 'pro',
    name: 'Power User',
    price: 9.99,
    features: ['10GB Storage', '100K API calls/month', 'Priority support']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 99.99,
    features: ['Unlimited Storage', 'Unlimited API calls', '24/7 support']
  }
];

export default function SignupPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const stripe = useStripe();
  const elements = useElements();
  
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('free');
  const [sessionInfo, setSessionInfo] = useState(null);
  
  const { register, handleSubmit, formState: { errors } } = useForm();
  
  // Extract URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const sessionId = urlParams.get('session');
    const plugin = urlParams.get('plugin');
    
    if (sessionId && plugin) {
      setSessionInfo({
        sessionId,
        plugin: plugin.charAt(0).toUpperCase() + plugin.slice(1)
      });
    }
  }, [location]);
  
  const onSubmit = async (data) => {
    if (!stripe || !elements) {
      toast.error('Stripe not loaded');
      return;
    }
    
    setLoading(true);
    
    try {
      let paymentMethod = null;
      
      // Create payment method if not free plan
      if (selectedPlan !== 'free') {
        const cardElement = elements.getElement(CardElement);
        const { error, paymentMethod: pm } = await stripe.createPaymentMethod({
          type: 'card',
          card: cardElement,
          billing_details: {
            name: data.fullName,
            email: data.email,
          },
        });
        
        if (error) {
          toast.error(error.message);
          setLoading(false);
          return;
        }
        
        paymentMethod = pm;
      }
      
      // Complete signup
      const response = await axios.post('/api/v1/signup/complete', {
        session_id: sessionInfo?.sessionId,
        email: data.email,
        full_name: data.fullName,
        plan: selectedPlan,
        stripe_payment_method: paymentMethod?.id
      });
      
      if (response.data.success) {
        toast.success('Account created successfully!');
        
        // Show success message with next steps
        setTimeout(() => {
          navigate('/dashboard', { 
            state: { 
              apiKey: response.data.api_key,
              userId: response.data.user_id 
            }
          });
        }, 2000);
      }
      
    } catch (error) {
      console.error('Signup error:', error);
      toast.error(error.response?.data?.error || 'Signup failed');
    }
    
    setLoading(false);
  };
  
  return (
    <Container>
      <Title>Welcome to MCP Memory Cloud</Title>
      
      {sessionInfo && (
        <PluginInfo>
          <h3>Setting up {sessionInfo.plugin} Plugin</h3>
          <p>Complete your account setup to start using AI memory across all your tools</p>
        </PluginInfo>
      )}
      
      <Subtitle>
        Get started with AI-powered memory that works across Claude, Cursor, ChatGPT, and more
      </Subtitle>
      
      <Form onSubmit={handleSubmit(onSubmit)}>
        <FormGroup>
          <Label>Full Name</Label>
          <Input
            {...register('fullName', { required: 'Name is required' })}
            placeholder="Enter your full name"
            className={errors.fullName ? 'error' : ''}
          />
          {errors.fullName && <ErrorText>{errors.fullName.message}</ErrorText>}
        </FormGroup>
        
        <FormGroup>
          <Label>Email Address</Label>
          <Input
            type="email"
            {...register('email', { 
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address'
              }
            })}
            placeholder="Enter your email"
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <ErrorText>{errors.email.message}</ErrorText>}
        </FormGroup>
        
        <FormGroup>
          <Label>Choose Your Plan</Label>
          <PricingCards>
            {PRICING_PLANS.map(plan => (
              <PricingCard
                key={plan.id}
                selected={selectedPlan === plan.id}
                onClick={() => setSelectedPlan(plan.id)}
              >
                <h4>{plan.name}</h4>
                <p><strong>${plan.price}/mo</strong></p>
                <small>{plan.features[0]}</small>
              </PricingCard>
            ))}
          </PricingCards>
        </FormGroup>
        
        {selectedPlan !== 'free' && (
          <FormGroup>
            <Label>Payment Information</Label>
            <CardWrapper>
              <CardElement
                options={{
                  style: {
                    base: {
                      fontSize: '16px',
                      color: '#424770',
                      '::placeholder': {
                        color: '#aab7c4',
                      },
                    },
                  },
                }}
              />
            </CardWrapper>
          </FormGroup>
        )}
        
        <Button type="submit" disabled={loading || !stripe}>
          {loading ? 'Creating Account...' : 
           selectedPlan === 'free' ? 'Create Free Account' : 
           `Subscribe to ${PRICING_PLANS.find(p => p.id === selectedPlan)?.name} - $${PRICING_PLANS.find(p => p.id === selectedPlan)?.price}/mo`}
        </Button>
      </Form>
    </Container>
  );
} 