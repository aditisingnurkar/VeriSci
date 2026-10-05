export const mockData = {
  claim: "Vaccines cause infertility.",
  verdict: "LIKELY CONTRADICTED",
  verdictConfidence: 96,
  supportingCount: 0,
  contradictingCount: 14,
  neutralCount: 2,
  explanation: "Based on the retrieved scientific literature, there is no evidence to support the claim that vaccines cause infertility. Multiple large-scale studies strongly contradict this assertion, showing no significant difference in fertility rates between vaccinated and unvaccinated populations.",
  evidence: [
    {
      id: "ev-1",
      title: "Systematic review of COVID-19 vaccination and fertility",
      snippet: "Our comprehensive analysis of clinical data indicates no negative impact of the SARS-CoV-2 vaccine on male or female fertility parameters.",
      prediction: "CONTRADICT",
      confidence: 98,
      relevanceScore: 0.92,
      source: "Journal of Medical Evidence, 2023"
    },
    {
      id: "ev-2",
      title: "Impact of vaccines on reproductive health: A longitudinal study",
      snippet: "Pregnancy rates were identical among the vaccinated cohort compared to the placebo group. No evidence of infertility was observed.",
      prediction: "CONTRADICT",
      confidence: 95,
      relevanceScore: 0.89,
      source: "Reproductive Health Sciences, 2022"
    },
    {
      id: "ev-3",
      title: "Vaccine components and biological markers",
      snippet: "We analyzed the biological markers post-vaccination. The study focused on immune response rather than reproductive outcomes.",
      prediction: "NEUTRAL",
      confidence: 82,
      relevanceScore: 0.65,
      source: "Immunology Letters, 2021"
    },
    {
      id: "ev-4",
      title: "Self-reported adverse events following immunization",
      snippet: "While some temporary side effects like fever were reported, subsequent follow-ups showed no long-term fertility issues.",
      prediction: "CONTRADICT",
      confidence: 91,
      relevanceScore: 0.78,
      source: "Global Health Journal, 2022"
    }
  ]
};

export const exampleClaims = [
  "Vaccines cause infertility.",
  "High doses of Vitamin C cure the common cold.",
  "Climate change is accelerating due to human carbon emissions.",
  "Eating artificial sweeteners increases the risk of cancer."
];
