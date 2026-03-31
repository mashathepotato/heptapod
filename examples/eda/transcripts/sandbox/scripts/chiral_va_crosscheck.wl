
(* ============================================================= *)
(* Chiral <-> VA cross-check for all dual-basis vertex families  *)
(* ============================================================= *)

(* Basis change relations:
   SFF: gS = (gL+gR)/2,  gP = (gR-gL)/2
        => Conjugate[gS] = (Conjugate[gL]+Conjugate[gR])/2, etc.
   VFF: gV = (gL+gR)/2,  gA = (gL-gR)/2
        => same pattern for conjugates
   Tensor: single g -> gL=gR=g in chiral => sum gives 2g
           Actually tensor has g, tensor-chiral has gL,gR
           Setting gL=g, gR=g in tensor-chiral should give tensor result *)

resultsDir = "/path/to/redacted";

readResult[name_String, key_String] := Module[{data},
  data = Import[resultsDir <> name <> "_results.json", "RawJSON"];
  ToExpression[data[key]]
];

(* --- 1. S -> f fbar: scalar-va vs scalar-chiral --- *)
Print["=== S -> f fbar: scalar-va vs scalar-chiral ==="];

widthSffVA = readResult["S_to_ff_scalarva", "width"];
widthSffCh = readResult["S_to_ff_chiral", "width"];

(* Substitute gS=(gL+gR)/2, gP=(gR-gL)/2 into VA result *)
subSFF = {gS -> (gL+gR)/2, gP -> (gR-gL)/2, 
          Conjugate[gS] -> (Conjugate[gL]+Conjugate[gR])/2,
          Conjugate[gP] -> (Conjugate[gR]-Conjugate[gL])/2};
widthSffVA2 = widthSffVA /. subSFF;
diff1 = FullSimplify[widthSffVA2 - widthSffCh];
Print["Difference (should be 0): ", diff1];

(* --- 2. f1 -> S f2bar: scalar-va vs scalar-chiral --- *)
Print["\n=== f1 -> S f2bar: scalar-va vs scalar-chiral ==="];

widthFSfVA = readResult["f_to_Sf_scalarva", "width"];
widthFSfCh = readResult["f_to_Sf_chiral", "width"];

(* Same basis change but use mf2bar consistently *)
widthFSfVA2 = widthFSfVA /. subSFF;
diff2 = FullSimplify[widthFSfVA2 - widthFSfCh];
Print["Difference (should be 0): ", diff2];

(* --- 3. f1 -> V f2bar: va vs chiral --- *)
Print["\n=== f1 -> V f2bar: va vs vector-chiral ==="];

widthFVfVA = readResult["f_to_Vf_va", "width"];
widthFVfCh = readResult["f_to_Vf_chiral", "width"];

subVFF = {gV -> (gL+gR)/2, gA -> (gL-gR)/2,
          Conjugate[gV] -> (Conjugate[gL]+Conjugate[gR])/2,
          Conjugate[gA] -> (Conjugate[gL]-Conjugate[gR])/2};
widthFVfVA2 = widthFVfVA /. subVFF;
diff3 = FullSimplify[widthFVfVA2 - widthFVfCh];
Print["Difference (should be 0): ", diff3];

(* --- 4. V -> f fbar: va vs chiral --- *)
Print["\n=== V -> f fbar: va vs vector-chiral ==="];

widthVffVA = readResult["V_to_ff_va", "width"];
widthVffCh = readResult["V_to_ff_chiral", "width"];

widthVffVA2 = widthVffVA /. subVFF;
diff4 = FullSimplify[widthVffVA2 - widthVffCh];
Print["Difference (should be 0): ", diff4];

(* --- 5. f1 -> V f2bar: tensor vs tensor-chiral (gL=gR=g) --- *)
Print["\n=== f1 -> V f2bar: tensor vs tensor-chiral (gL=gR=g) ==="];

widthFVfT = readResult["f_to_Vf_tensor", "width"];
widthFVfTCh = readResult["f_to_Vf_tensorchiral", "width"];

widthFVfTCh2 = widthFVfTCh /. {gL -> g, gR -> g, 
                                Conjugate[gL] -> Conjugate[g],
                                Conjugate[gR] -> Conjugate[g]};
diff5 = FullSimplify[widthFVfTCh2 - widthFVfT];
Print["Difference (should be 0): ", diff5];

(* --- 6. V -> f fbar: tensor vs tensor-chiral (gL=gR=g) --- *)
Print["\n=== V -> f fbar: tensor vs tensor-chiral (gL=gR=g) ==="];

widthVffT = readResult["V_to_ff_tensor_v2", "width"];
widthVffTCh = readResult["V_to_ff_tensorchiral", "width"];

widthVffTCh2 = widthVffTCh /. {gL -> g, gR -> g,
                                Conjugate[gL] -> Conjugate[g],
                                Conjugate[gR] -> Conjugate[g]};
diff6 = FullSimplify[widthVffTCh2 - widthVffT];
Print["Difference (should be 0): ", diff6];

Print["\n=== All cross-checks complete ==="];
Print["SYMBOLIC_RESULT[crosscheck_summary]: ", {diff1, diff2, diff3, diff4, diff5, diff6}];
