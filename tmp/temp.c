void SBML_compute_simulation(pScore result, Model_t *mod, double *reactions_ratio, gsl_rng * r, char **banned, int nbBanned)
{
  /* Simulation du reseau metabolique  */
  int i, temp = 1;
  pEspeces molecules=NULL;
  pTestReaction TR=NULL;

  /* Allocation memoire */
  TR=(pTestReaction)malloc(1*sizeof(TestReaction));
  assert(TR!=NULL);

  /* File information */
  molecules = Especes_alloc(result->tailleSpecies);

  /* Initialisation de la quantite des especes */
  SBML_initEspeceAmounts(mod, molecules, result->tailleSpecies);

  /* Initialisation des reactions et des ratios*/
  SBML_setReactions(mod, molecules, result, reactions_ratio, result->tailleReactions, result->tailleSpecies);

  /* Simulation des reactions */
  while (temp > END) {
      temp = 0;
      for (i = 0; i < result->tailleSpecies; i++) {
          temp +=SBML_simulate(mod, molecules, r, TR, banned, nbBanned, result->tailleSpecies, i);
      }
  }

  /*Score */
  SBML_score(mod, molecules, result, reactions_ratio, result->tailleReactions, result->tailleSpecies);

  /* Liberation de la memoire de la structure Especes */
  Especes_free(molecules, result->tailleSpecies);
  if(TR!=NULL) free(TR);
}

int SBML_simulate(Model_t *mod, pEspeces molecules, const gsl_rng * r, pTestReaction T, char **banned, int nbBanned, int nbEspeces, int ref)
{
  Reaction_t *react=NULL;
  int i, minStep = 0, valid=0, nbReactions = 0;

  /* Probleme ATP, ADP, NADH, NAD+ */
  for(i=0;i<nbBanned;i++){
      if(!strcmp(molecules[ref].id,banned[i])) return END;
  }
  /* Decompte du nombre de reaction */
  /*nbReactions = Especes_getNbreactions(molecules, ref);*/
  nbReactions = molecules[ref].nbReactions
  printf("nbreactions %d struct %d\n",nbReactions,molecules[ref].nbReactions);
  /* Variation selon le cas. */
  switch (nbReactions) {
  /* Cas ou aucune reaction n'est possible */
  case 0:
    return END;
    break;
  /* Cas ou une seule reaction est possible */
  case 1:
    react = molecules[ref].system->link;
    if ((minStep = SBML_checkQuantite(mod, react, nbEspeces, molecules))<= END)
      return END;
    /* Tant qu'il reste des molecules, on realise la reaction */
    while (minStep > 0) {
        SBML_reaction(mod, molecules,  react, nbEspeces);
        minStep--;
    }
    break;
  /* Cas ou  plusieurs reactions sont possibles*/
  default:
    /* Allocation de la memoire au tableau des reactions */
    SBML_allocTest(T, nbReactions);
    /* Estimation du nombre de reaction realisable */
    valid = SBML_EstimationReaction(mod, T, molecules, ref, nbEspeces);
    /* Il n'y a plus de reactions realisables */
    if(valid<=END){
        SBML_freeTest(T);
        return END;
    }
    /* On realise les reactions */
    while(Especes_getQuantite(molecules, ref)> 0.0 && valid>END) {
        react = SBML_reactChoice(molecules, r, ref);
        SBML_reaction(mod, molecules,  react, nbEspeces);
        valid--;
    }
    /* Liberation de la memoire allouee au tableau des reactions */
    SBML_freeTest(T);
    break;
  }
  return PURSUE;
}

void SBML_reaction(Model_t *mod, pEspeces molecules, Reaction_t *react, int nbEspeces)
{
  /* Simulation d'une transision discrete */
  SpeciesReference_t *reactif;
  Species_t *especeId;
  int i, ref = 0;

  /*boucle pour retirer des reactifs*/
  for (i = 0; i < (int)Reaction_getNumReactants(react); i++) {
      /* Indentification du reactif */
      reactif = Reaction_getReactant(react, i);
      especeId = Model_getSpeciesById(mod, SpeciesReference_getSpecies(reactif));
      ref = Especes_find(molecules, Species_getId(especeId), nbEspeces);
      /* Modification de sa quantite */
      Especes_setQuantite(molecules, ref, (Especes_getQuantite(molecules, ref)- SpeciesReference_getStoichiometry(reactif)));
  }

  /*boucle pour ajouter des produits */
  for (i = 0; i < (int)Reaction_getNumProducts(react); i++) {
      /* Indentification du reactif */
      reactif = Reaction_getProduct(react, i);
      especeId = Model_getSpeciesById(mod, SpeciesReference_getSpecies(reactif));
      ref = Especes_find(molecules, Species_getId(especeId), nbEspeces);
      /* Modification de sa quantite */
      Especes_setQuantite(molecules, ref, (Especes_getQuantite(molecules, ref)+ SpeciesReference_getStoichiometry(reactif)));
  }
}

Reaction_t * SBML_reactChoice(pEspeces molecules, const gsl_rng * r, int ref)
{
  /* Determine aleatoirement la reaction a realiser pour les noeuds de plusieurs reactions */
  pReaction temp = NULL;
  pReaction Q = molecules[ref].system;
  double value = gsl_rng_uniform(r) * 100.0;
  double choice = 0.0;

  /* Si la valeur choisie est inferieure au ratio alloue a la premiere reaction du noeud */
  if(value<Q->ratio) temp=Q;

  /* Cas ou il faut ajouter les ratio des autres reactions du noeud */
  else{
      do {
          choice += Q->ratio;
          Q = Q->suivant;
          temp=Q;
      }while (Q->suivant != NULL && value <= (choice + Q->suivant->ratio) && value > choice);
  }

  /* Temp n'indique aucune reaction */
  if(temp==NULL){
      fprintf(stderr,"There is something wrong with the ratio data\n");
      exit(EXIT_FAILURE);
  }
  /* retourne la reaction choisie */
  return (temp->link);
}

int SBML_checkQuantite(Model_t *mod, Reaction_t *react, int nbEspeces, pEspeces molecules)
{
  /* Determine le nombre de reaction possible a partir de la quantite des reactifs */
  int  ref = 0, i;
  double quantite = 0.0, minStep = 0.0, temp = 0.0;
  SpeciesReference_t *reactif;
  Species_t *especeId;
  /*TODO Il est possible de reprogrammer ca plus proprement */
  /* Recupere la quantite de la premiere molecule */
  reactif = Reaction_getReactant(react, 0);
  especeId = Model_getSpeciesById(mod, SpeciesReference_getSpecies(reactif));
  ref = Especes_find(molecules, Species_getId(especeId), nbEspeces);
  /* Cas ou la quantite de la molecule est egale a zero */
  if ((quantite = Especes_getQuantite(molecules, ref)) <= 0.0) return END;
  /* Calcul du nombre de pas minimum qu'il sera possible d'effectuer */
  /* C'est le nombre minimum d'etat de tous les reactifs qui determine le nombre de pas */
  minStep = floor(quantite / SpeciesReference_getStoichiometry(reactif));

  /*fprintf(stderr,"round species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),round(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));
  fprintf(stderr,"ceil species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),ceil(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));
  fprintf(stderr,"floor species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),floor(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));*/
  /* Cas ou le nombre de pas est egal a 0 */
  if(minStep==0.0) return END;

  /* On calcule pour les autres reactifs */
  for (i = 1; i < (int)Reaction_getNumReactants(react); i++) {
      /* Recupere la quantite d'une molecule */
      reactif = Reaction_getReactant(react, i);
      especeId = Model_getSpeciesById(mod, SpeciesReference_getSpecies(reactif));
      ref = Especes_find(molecules, Species_getId(especeId), nbEspeces);
      quantite= Especes_getQuantite(molecules, ref);
      /* La quantite est egale a 0 */
      if(quantite<=0.0) return END;
      /* On calcule le nombre de pas minimum qu'il sera possible d'effectuer */
      temp = floor(Especes_getQuantite(molecules, ref)/SpeciesReference_getStoichiometry(reactif));
      /*fprintf(stderr,"species %s minstep %f temp %f\n",Species_getId(especeId),minStep,temp);*/
      /*fprintf(stderr,"round species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),round(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));
      fprintf(stderr,"ceil species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),ceil(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));
      fprintf(stderr,"floor species %s minstep %f quantite %f stochiometry %f\n",Species_getId(especeId),floor(quantite / SpeciesReference_getStoichiometry(reactif)),quantite,SpeciesReference_getStoichiometry(reactif));*/
      /* Cas ou le nombre de pas est egal a 0 */
      if(temp==0.0) return END;
      /* Si le nouveau nombre est inferieur au precedent, on change la valeur de minStep */
      if (minStep > temp) minStep = temp;
  }
  /*fprintf(stderr,"minStep returned %d\n",(int)minStep);*/
  return (int)minStep;
}