import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { userRepository } from '../repositories/user.repository.js';
import { config } from '../config/env.js';
import { ApiError } from '../utils/apiError.js';

export const authService = {
  async register({ email, password, name }) {
    const existingUser = await userRepository.findByEmail(email);
    if (existingUser) {
      throw ApiError.badRequest('An account with this email address already exists.');
    }

    const salt = await bcrypt.genSalt(12);
    const passwordHash = await bcrypt.hash(password, salt);

    const user = await userRepository.create({
      email,
      passwordHash,
      name
    });

    const tokens = this.generateTokens(user);

    return {
      user: {
        id: user._id.toString(),
        email: user.email,
        name: user.name,
        role: user.role,
        createdAt: user.createdAt
      },
      tokens
    };
  },

  async login({ email, password }) {
    const user = await userRepository.findByEmail(email);
    if (!user) {
      throw ApiError.unauthorized('Invalid email or password credentials.');
    }

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
      throw ApiError.unauthorized('Invalid email or password credentials.');
    }

    const tokens = this.generateTokens(user);

    return {
      user: {
        id: user._id.toString(),
        email: user.email,
        name: user.name,
        role: user.role,
        createdAt: user.createdAt
      },
      tokens
    };
  },

  generateTokens(user) {
    const payload = {
      id: user._id.toString(),
      sub: user._id.toString(),
      email: user.email,
      role: user.role
    };

    const accessToken = jwt.sign(payload, config.jwt.accessSecret, {
      expiresIn: config.jwt.accessExpiresIn
    });

    const refreshToken = jwt.sign(payload, config.jwt.refreshSecret, {
      expiresIn: config.jwt.refreshExpiresIn
    });

    return {
      accessToken,
      refreshToken,
      expiresIn: 900 // 15 minutes
    };
  }
};

