import { User } from '../models/user.model.js';

export const userRepository = {
  async findById(id) {
    return User.findById(id).exec();
  },

  async findByEmail(email) {
    return User.findOne({ email: email.toLowerCase() }).exec();
  },

  async create(userData) {
    const user = new User(userData);
    return user.save();
  },

  async updateById(id, updateData) {
    return User.findByIdAndUpdate(id, updateData, { new: true }).exec();
  }
};

