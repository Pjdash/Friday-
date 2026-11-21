import type { Profile } from "./types";

/**
 * Fictional people for trying the tool. Derived from the shape of the demo fixtures
 * (tests/fixtures/citizens_diverse.csv) but with no names, phone numbers or ids, so no real or
 * pseudo-real person data ships in the UI.
 */
export interface Sample {
  id: string;
  label: Record<"en" | "hi" | "kn" | "ta", string>;
  profile: Required<Profile>;
}

export const SAMPLES: Sample[] = [
  {
    id: "small-farmer",
    label: {
      en: "Small farmer, 2.2 acres",
      hi: "छोटा किसान, 2.2 एकड़",
      kn: "ಸಣ್ಣ ರೈತ, 2.2 ಎಕರೆ",
      ta: "சிறு விவசாயி, 2.2 ஏக்கர்",
    },
    profile: {
      age: 44,
      annual_household_income: 115000,
      occupation: "farmer",
      land_holding_acres: 2.2,
      residence_type: "rural",
      category: "obc",
    },
  },
  {
    id: "retired-urban",
    label: {
      en: "Retired, age 68",
      hi: "सेवानिवृत्त, आयु 68",
      kn: "ನಿವೃತ್ತ, ವಯಸ್ಸು 68",
      ta: "ஓய்வு பெற்றவர், வயது 68",
    },
    profile: {
      age: 68,
      annual_household_income: 138000,
      occupation: "retired",
      land_holding_acres: 0,
      residence_type: "urban",
      category: "general",
    },
  },
  {
    id: "st-farmer",
    label: {
      en: "ST farmer, 3.8 acres",
      hi: "ST किसान, 3.8 एकड़",
      kn: "ST ರೈತ, 3.8 ಎಕರೆ",
      ta: "ST விவசாயி, 3.8 ஏக்கர்",
    },
    profile: {
      age: 57,
      annual_household_income: 125000,
      occupation: "farmer",
      land_holding_acres: 3.8,
      residence_type: "rural",
      category: "st",
    },
  },
  {
    id: "large-farmer",
    label: {
      en: "Farmer, 6.4 acres",
      hi: "किसान, 6.4 एकड़",
      kn: "ರೈತ, 6.4 ಎಕರೆ",
      ta: "விவசாயி, 6.4 ஏக்கர்",
    },
    profile: {
      age: 51,
      annual_household_income: 280000,
      occupation: "farmer",
      land_holding_acres: 6.4,
      residence_type: "rural",
      category: "general",
    },
  },
];
